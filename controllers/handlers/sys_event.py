# coding=utf-8
import logging

from werobot.reply import create_reply
from .. import client
from openerp.http import request

_logger = logging.getLogger(__name__)

def main(robot):

    @robot.subscribe
    def subscribe(message):
        _logger.info('>>> wx msg: %s', message.__dict__)
        from .. import client
        entry = client.wxenv(request.env)
        serviceid = message.target
        openid = message.source

        info = entry.wxclient.get_user_info(openid)
        info['group_id'] = str(info['groupid'])
        env = request.env()
        rs = env['wx.user'].sudo().search( [('openid', '=', openid)] )
        if not rs.exists():
            qrscene = message.__dict__.get('EventKey')
            if qrscene:
                inviter_id = qrscene.split('=')[1]
                info['inviter_id'] = int(inviter_id)
            env['wx.user'].sudo().create(info)
        else:
            rs.write({'subscribe': True})

        if entry.subscribe_auto_msg:
            ret_msg = entry.subscribe_auto_msg
        else:
            ret_msg = "您终于来了！欢迎关注"

        return entry.create_reply(ret_msg, message)

    @robot.unsubscribe
    def unsubscribe(message):

        serviceid = message.target
        openid = message.source
        env = request.env()
        rs = env['wx.user'].sudo().search( [('openid', '=', openid)] )
        if rs.exists():
            rs.write({'subscribe': False})

        return ""

    @robot.view
    def url_view(message):
        print('obot.view---------%s'%message)
