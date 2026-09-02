# -*- coding: utf-8 -*-
"""
openGauss 简易客户端
====================
openGauss 使用自定义的 SHA256 认证（AUTH_REQ_SHA256=10），标准 PostgreSQL
驱动（psycopg2/psycopg）无法连接。此脚本按 openGauss 官方算法手工实现了认证。

用法:
    python opengauss_client.py "SELECT count(*) FROM s_tpf.sys_user"
    python opengauss_client.py -l          # 列出 s_tpf 模式下的所有表

依赖: 仅 Python 标准库。
"""
import socket
import struct
import hashlib
import hmac
import sys

HOST = "118.126.107.174"
PORT = 5432
DB = "db_tpcc"
SCHEMA = "s_tpf"           # URL 里的 currentSchema
USER = "sanz_user"
PASSWORD = "Sanz@202608"
ITERATION = 10000          # openGauss ITERATION_COUNT，协议 3.0 时服务端不返回迭代次数


class OGClient:
    def __init__(self, host=HOST, port=PORT, db=DB, user=USER, password=PASSWORD):
        self.s = socket.create_connection((host, port), timeout=20)
        self._auth(db, user, password)

    def _read_msg(self):
        hdr = b""
        while len(hdr) < 5:
            c = self.s.recv(5 - len(hdr))
            if not c:
                return None, None
            hdr += c
        typ, ln = hdr[0:1], struct.unpack("!I", hdr[1:5])[0]
        payload = b""
        while len(payload) < ln - 4:
            c = self.s.recv(ln - 4 - len(payload))
            if not c:
                break
            payload += c
        return typ, payload

    def _send(self, typ, payload):
        self.s.sendall(typ + struct.pack("!I", len(payload) + 4) + payload)

    def _auth(self, db, user, password):
        params = {"user": user, "database": db, "client_encoding": "UTF8"}
        body = b"".join(k.encode() + b"\x00" + v.encode() + b"\x00"
                        for k, v in params.items()) + b"\x00"
        self.s.sendall(struct.pack("!I", len(body) + 8) + struct.pack("!I", 196608) + body)

        typ, payload = self._read_msg()
        code = struct.unpack("!I", payload[:4])[0]
        if code != 10:  # AUTH_REQ_SHA256
            raise RuntimeError(f"unexpected auth request code: {code}")

        # 报文: int32(SHA256_PASSWORD=2) + salt_hex(64) + token_hex(8) + server_sig_hex(64)
        salt = bytes.fromhex(payload[8:72].decode())
        token = bytes.fromhex(payload[72:80].decode())

        k = hashlib.pbkdf2_hmac("sha1", password.encode(), salt, ITERATION, 32)
        client_key = hmac.new(k, b"Client Key", hashlib.sha256).digest()
        stored_key = hashlib.sha256(client_key).digest()
        client_sig = hmac.new(stored_key, token, hashlib.sha256).digest()
        proof = bytes(a ^ b for a, b in zip(client_key, client_sig))

        self._send(b"p", proof.hex().encode())
        while True:
            typ, payload = self._read_msg()
            if typ == b"E":
                raise RuntimeError("auth failed: " + payload[4:].decode(errors="replace"))
            if typ == b"R" and struct.unpack("!I", payload[:4])[0] == 0:
                break  # AUTH_OK
        while True:
            typ, payload = self._read_msg()
            if typ == b"Z":
                break  # ReadyForQuery

    def query(self, sql):
        """执行查询，返回 (列名列表, 行列表)。"""
        self._send(b"Q", sql.encode() + b"\x00")
        cols, rows = [], []
        while True:
            typ, payload = self._read_msg()
            if typ == b"T":  # RowDescription
                n = struct.unpack("!H", payload[:2])[0]
                off, cols = 2, []
                for _ in range(n):
                    nl = payload.index(b"\x00", off)
                    cols.append(payload[off:nl].decode())
                    off = nl + 1 + 18
            elif typ == b"D":  # DataRow
                n = struct.unpack("!H", payload[:2])[0]
                off, row = 2, []
                for _ in range(n):
                    ln = struct.unpack("!I", payload[off:off + 4])[0]
                    off += 4
                    if ln == 0xFFFFFFFF:  # NULL 标记（无符号 4294967295）
                        row.append(None)
                    else:
                        row.append(payload[off:off + ln].decode(errors="replace"))
                        off += ln
                rows.append(tuple(row))
            elif typ == b"C":
                pass
            elif typ == b"E":
                raise RuntimeError(payload[4:].decode(errors="replace"))
            elif typ == b"Z":
                break
        return cols, rows

    def close(self):
        self.s.close()


def print_table(cols, rows, limit=None):
    if limit and len(rows) > limit:
        rows = rows[:limit]
    print(" | ".join(cols))
    print("-" * 60)
    for r in rows:
        print(" | ".join("" if v is None else str(v) for v in r))
    if len(rows) >= 1:
        print(f"(显示 {len(rows)} 行)")


if __name__ == "__main__":
    c = OGClient()
    try:
        if len(sys.argv) > 1 and sys.argv[1] in ("-l", "--list"):
            _, rows = c.query(
                f"SELECT table_name FROM information_schema.tables "
                f"WHERE table_schema = '{SCHEMA}' ORDER BY table_name")
            print(f"schema {SCHEMA} 下的表 ({len(rows)}):")
            for (t,) in rows:
                print("  " + t)
        else:
            sql = sys.argv[1] if len(sys.argv) > 1 else "SELECT version()"
            cols, rows = c.query(sql)
            print_table(cols, rows, limit=200)
    finally:
        c.close()
