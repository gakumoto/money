"""ネットワーク復帰待ち。Modern Standby / スリープ復帰直後の DNS 不安定対策。

Windows 11 の Modern Standby (S0 低電力アイドル) からタスクスケジューラで起動された
直後は Wi-Fi の再接続に十数秒〜数分かかるケースがある。
本処理を実行する前に DNS が引ける状態を待つことで、

    NameResolutionError: Failed to resolve 'graph.threads.net' (getaddrinfo failed)

を回避する。

使い方:
    from _net_wait import wait_for_network
    wait_for_network()  # graph.threads.net が引けるまで最大3分待つ
"""
from __future__ import annotations

import socket
import sys
import time


def wait_for_network(
    host: str = "graph.threads.net",
    max_wait: int = 180,
    interval: float = 3.0,
) -> bool:
    """指定ホストの DNS が引けるまで最大 max_wait 秒待つ.

    Returns:
        True: DNS 解決成功
        False: タイムアウト (max_wait 秒待っても引けなかった)
    """
    deadline = time.monotonic() + max_wait
    attempt = 0
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        attempt += 1
        try:
            socket.gethostbyname(host)
            if attempt > 1:
                print(
                    f"[net_wait] OK: {host} 解決成功 ({attempt}回目)",
                    file=sys.stderr,
                )
            return True
        except OSError as e:
            last_err = e
            time.sleep(interval)
    print(
        f"[net_wait] NG: {host} のDNS解決に {max_wait}秒待っても失敗: {last_err}",
        file=sys.stderr,
    )
    return False


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "graph.threads.net"
    ok = wait_for_network(host=host)
    sys.exit(0 if ok else 1)
