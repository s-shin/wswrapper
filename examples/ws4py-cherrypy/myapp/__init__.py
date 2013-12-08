# -*- coding: utf-8 -*-

def setup_argparser(parser):
    """コマンドパーサーのセットアップ。
    パーサーは共有されるので、被らないように上手く調整すること。
    
    :param parser: ``argparse.ArgumentParser`` のインスタンス。
    """
    pass


def setup_app(args):
    """コマンドパース後のセットアップ。
    
    :param args: ``parser.arg_parse()`` の戻り値。
    """
    pass


def on_open(client):
    """WebSocketのコネクションが成立した時に呼ばれる。
    """
    pass


def on_close(client):
    """WebSocketのコネクションが切れた時に呼ばれる。
    """
    pass
    
    
def on_setup(client, data):
    client.emit("print", "Hello world!")


