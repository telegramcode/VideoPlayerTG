#!/usr/bin/env python3
# Copyright (C) @owogram
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from utils import LOGGER
from pyrogram import Client
from contextlib import suppress
from config import Config
from asyncio import sleep
import datetime
import pytz
import calendar
from utils import (
    cancel_all_schedules,
    delete_messages,
    get_admins, 
    get_buttons, 
    get_playlist_str,
    leave_call, 
    mute, 
    pause,
    recorder_settings, 
    restart, 
    restart_playout, 
    resume,
    schedule_a_play, 
    seek_file, 
    set_config, 
    settings_panel, 
    shuffle_playlist, 
    skip,
    start_record_stream,
    stop_recording,
    sync_to_db, 
    unmute,
    volume,
    volume_buttons
    )
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery
)
from pyrogram.errors import (
    MessageNotModified,
    MessageIdInvalid,
    QueryIdInvalid
)
from pyrogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)

IST = pytz.timezone(Config.TIME_ZONE)

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    with suppress(MessageIdInvalid, MessageNotModified, QueryIdInvalid):
        admins = await get_admins(Config.CHAT)
        if query.data.startswith("info"):
            me, you = query.data.split("_")
            text="Join @owogram"
            if you == "volume":
                await query.answer()
                await query.message.edit_reply_markup(reply_markup=await volume_buttons())
                return
            if you == "player":
                if not Config.CALL_STATUS:
                    return await query.answer("Kh??ng ch??i g?? c???.", show_alert=True)
                await query.message.edit_reply_markup(reply_markup=await get_buttons())
                await query.answer()
                return
            if you == "video":
                text="Chuy???n bot c???a b???n sang Tr??nh ph??t video / ??m thanh."
            elif you == "shuffle":
                text="B???t ho???c t???t t??nh n??ng ph??t ng???u nhi??n danh s??ch ph??t t??? ?????ng"
            elif you == "admin":
                text="B???t ????? h???n ch??? l???nh ph??t ch??? d??nh cho qu???n tr??? vi??n."
            elif you == "mode":
                text="B???t Ph??t l???i kh??ng ng???ng s??? l??m cho tr??nh ph??t ch???y 24/7 v?? t??? ?????ng kh???i ?????ng khi kh???i ?????ng l???i. "
            elif you == "title":
                text="Cho ph??p ch???nh s???a ti??u ????? Tr?? chuy???n video th??nh ti??u ????? b??i h??t ??ang ph??t hi???n t???i."
            elif you == "reply":
                text="Ch???n c?? t??? ?????ng tr??? l???i tin nh???n cho userbot hay kh??ng. "
            elif you == "videorecord":
                text = "B???t ????? ghi c??? video v?? ??m thanh, n???u b??? t???t, ch??? ??m thanh s??? ???????c ghi l???i."
            elif you == "videodimension":
                text = "Ch???n k??ch th?????c c???a video quay"
            elif you == "rectitle":
                text = "Ti??u ????? t??y ch???nh cho b???n ghi ??m cu???c tr?? chuy???n c???a b???n, S??? d???ng l???nh /rtitle ????? ?????t ti??u ?????"
            elif you == "recdumb":
                text = "M???t k??nh m?? t???t c??? c??c b???n ghi ???????c chuy???n ti???p ?????n. ?????m b???o T??i kho???n ng?????i d??ng l?? qu???n tr??? vi??n ??? ????. ?????t m???t c??i b???ng c??ch s??? d???ng /env ho???c /config."
            await query.answer(text=text, show_alert=True)
            return


        elif query.data.startswith("help"):
            if query.message.chat.type != "private" and query.message.reply_to_message.from_user is None:
                return await query.answer("T??i kh??ng th??? gi??p b???n ??? ????y, v?? b???n l?? qu???n tr??? vi??n ???n danh, h??y nh???n tin cho t??i trong cu???c tr?? chuy???n ri??ng t??.", show_alert=True)
            elif query.message.chat.type != "private" and query.from_user.id != query.message.reply_to_message.from_user.id:
                return await query.answer("Okda", show_alert=True)
            me, nyav = query.data.split("_")
            back=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Back", callback_data="help_main"),
                        InlineKeyboardButton("Close", callback_data="close"),
                    ],
                ]
                )
            if nyav == 'main':
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(f"Play", callback_data='help_play'),
                            InlineKeyboardButton(f"C??i ?????t", callback_data=f"help_settings"),
                            InlineKeyboardButton(f"Ghi l???i", callback_data='help_record'),
                        ],
                        [
                            InlineKeyboardButton("L???p l???ch tr??nh", callback_data="help_schedule"),
                            InlineKeyboardButton("Ki???m so??t", callback_data='help_control'),
                            InlineKeyboardButton("Admins", callback_data="help_admin"),
                        ],
                        [
                            InlineKeyboardButton(f"Linh tinh", callback_data='help_misc'),
                            InlineKeyboardButton("C???u h??nh vars", callback_data='help_env'),
                            InlineKeyboardButton("Close", callback_data="close"),
                        ],
                    ]
                    )
                await query.message.edit("Hi???n th??? menu tr??? gi??p, Ch???n t??? c??c t??y ch???n b??n d?????i.", reply_markup=reply_markup, disable_web_page_preview=True)
            elif nyav == 'play':
                await query.message.edit(Config.PLAY_HELP, reply_markup=back, disable_web_page_preview=True)
            elif nyav == 'settings':
                await query.message.edit(Config.SETTINGS_HELP, reply_markup=back, disable_web_page_preview=True)
            elif nyav == 'schedule':
                await query.message.edit(Config.SCHEDULER_HELP, reply_markup=back, disable_web_page_preview=True)
            elif nyav == 'control':
                await query.message.edit(Config.CONTROL_HELP, reply_markup=back, disable_web_page_preview=True)
            elif nyav == 'admin':
                await query.message.edit(Config.ADMIN_HELP, reply_markup=back, disable_web_page_preview=True)
            elif nyav == 'misc':
                await query.message.edit(Config.MISC_HELP, reply_markup=back, disable_web_page_preview=True)
            elif nyav == 'record':
                await query.message.edit(Config.RECORDER_HELP, reply_markup=back, disable_web_page_preview=True)
            elif nyav == 'env':
                await query.message.edit(Config.ENV_HELP, reply_markup=back, disable_web_page_preview=True)
            return
            
        if not query.from_user.id in admins:
            await query.answer(
                "???? Played Joji.mp3",
                show_alert=True
                )
            return
        #scheduler stuffs
        if query.data.startswith("sch"):
            if query.message.chat.type != "private" and query.message.reply_to_message.from_user is None:
                return await query.answer("B???n kh??ng th??? s??? d???ng l???p l???ch ??? ????y, v?? b???n l?? qu???n tr??? vi??n ???n danh. L??n l???ch t??? cu???c tr?? chuy???n ri??ng t??.", show_alert=True)
            if query.message.chat.type != "private" and query.from_user.id != query.message.reply_to_message.from_user.id:
                return await query.answer("Okda", show_alert=True)
            data = query.data
            today = datetime.datetime.now(IST)
            smonth=today.strftime("%B")
            obj = calendar.Calendar()
            thisday = today.day
            year = today.year
            month = today.month
            if data.startswith("sch_month"):
                none, none , yea_r, month_, day = data.split("_")
                if yea_r == "choose":
                    year=int(year)
                    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                    button=[]
                    button_=[]
                    k=0
                    for month in months:
                        k+=1
                        year_ = year
                        if k < int(today.month):
                            year_ += 1
                            button_.append([InlineKeyboardButton(text=f"{str(month)}  {str(year_)}",callback_data=f"sch_showdate_{year_}_{k}")])
                        else:
                            button.append([InlineKeyboardButton(text=f"{str(month)}  {str(year_)}",callback_data=f"sch_showdate_{year_}_{k}")])
                    button = button + button_
                    button.append([InlineKeyboardButton("Close", callback_data="schclose")])
                    await query.message.edit("B??y gi??? Ch???n th??ng ????? l??n l???ch tr?? chuy???n tho???i??? ??????", reply_markup=InlineKeyboardMarkup(button))
                elif day == "none":
                    return
                else:
                    year = int(yea_r)
                    month = int(month_)
                    date = int(day)
                    datetime_object = datetime.datetime.strptime(str(month), "%m")
                    smonth = datetime_object.strftime("%B")
                    button=[]
                    if year == today.year and month == today.month and date == today.day:
                        now = today.hour
                    else:
                        now=0
                    l = list()
                    for i in range(now, 24):
                        l.append(i)
                    splited=[l[i:i + 6] for i in range(0, len(l), 6)]
                    for i in splited:
                        k=[]
                        for d in i:
                            k.append(InlineKeyboardButton(text=f"{d}",callback_data=f"sch_day_{year}_{month}_{date}_{d}"))
                        button.append(k)
                    if month == today.month and date < today.day and year==today.year+1:
                        pyear=year-1
                    else:
                        pyear=year
                    button.append([InlineKeyboardButton("Back", callback_data=f"sch_showdate_{pyear}_{month}"), InlineKeyboardButton("Close", callback_data="schclose")])
                    await query.message.edit(f"Choose the hour of {date} {smonth} {year} to schedule  a voicechat.", reply_markup=InlineKeyboardMarkup(button))

            elif data.startswith("sch_day"):
                none, none, year, month, day, hour = data.split("_")
                year = int(year)
                month = int(month)
                day = int(day)
                hour = int(hour)
                datetime_object = datetime.datetime.strptime(str(month), "%m")
                smonth = datetime_object.strftime("%B")
                if year == today.year and month == today.month and day == today.day and hour == today.hour:
                    now=today.minute
                else:
                    now=0
                button=[]
                l = list()
                for i in range(now, 60):
                    l.append(i)
                for i in range(0, len(l), 6):
                    chunk = l[i:i + 6]
                    k=[]
                    for d in chunk:
                        k.append(InlineKeyboardButton(text=f"{d}",callback_data=f"sch_minute_{year}_{month}_{day}_{hour}_{d}"))
                    button.append(k)
                button.append([InlineKeyboardButton("Back", callback_data=f"sch_month_{year}_{month}_{day}"), InlineKeyboardButton("Close", callback_data="schclose")])
                await query.message.edit(f"Ch???n ph??t trong s??? {hour}th gi??? tr??n {day} {smonth} {year} ????? l??n l???ch Voicechat.", reply_markup=InlineKeyboardMarkup(button))

            elif data.startswith("sch_minute"):
                none, none, year, month, day, hour, minute = data.split("_")
                year = int(year)
                month = int(month)
                day = int(day)
                hour = int(hour)
                minute = int(minute)
                datetime_object = datetime.datetime.strptime(str(month), "%m")
                smonth = datetime_object.strftime("%B")
                if year == today.year and month == today.month and day == today.day and hour == today.hour and minute <= today.minute:
                    await query.answer("T??i kh??ng c?? c??? m??y th???i gian ????? ??i v??? qu?? kh??? !!!.")
                    return 
                final=f"{day}th {smonth} {year} at {hour}:{minute}"
                button=[
                    [
                        InlineKeyboardButton("X??c nh???n", callback_data=f"schconfirm_{year}-{month}-{day} {hour}:{minute}"),
                        InlineKeyboardButton("Back", callback_data=f"sch_day_{year}_{month}_{day}_{hour}")
                    ],
                    [
                        InlineKeyboardButton("Close", callback_data="schclose")
                    ]
                ]
                data=Config.SCHEDULED_STREAM.get(f"{query.message.chat.id}_{query.message.message_id}")
                if not data:
                    await query.answer("L???ch tr??nh n??y ???? h???t h???n", show_alert=True)
                if data['3'] == "telegram":
                    title=data['1']
                else:
                    title=f"[{data['1']}]({data['2']})"
                await query.message.edit(f"Lu???ng c???a b???n {title} hi???n ???? ???????c l??n l???ch ????? b???t ?????u v??o {final}\n\nB???m X??c nh???n ????? x??c nh???n th???i gian.", reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview=True)                

            elif data.startswith("sch_showdate"):
                tyear=year
                none, none, year, month = data.split("_")
                datetime_object = datetime.datetime.strptime(month, "%m")
                thissmonth = datetime_object.strftime("%B")
                obj = calendar.Calendar()
                thisday = today.day
                year = int(year)
                month = int(month)
                m=obj.monthdayscalendar(year, month)
                button=[]
                button.append([InlineKeyboardButton(text=f"{str(thissmonth)}  {str(year)}",callback_data=f"sch_month_choose_none_none")])
                days=["Mon", "Tues", "Wed", "Thu", "Fri", "Sat", "Sun"]
                f=[]
                for day in days:
                    f.append(InlineKeyboardButton(text=f"{day}",callback_data=f"day_info_none"))
                button.append(f)
                for one in m:
                    f=[]
                    for d in one:
                        year_=year
                        if year==today.year and month == today.month and d < int(today.day):
                            year_ += 1
                        if d == 0:
                            k="\u2063"
                            d="none"
                        else:
                            k=d
                        f.append(InlineKeyboardButton(text=f"{k}",callback_data=f"sch_month_{year_}_{month}_{d}"))
                    button.append(f)
                button.append([InlineKeyboardButton("Close", callback_data="schclose")])
                await query.message.edit(f"Ch???n ng??y trong th??ng b???n mu???n l??n l???ch tr?? chuy???n tho???i.\nToday is {thisday} {smonth} {tyear}. Ch???n m???t ng??y tr?????c ng??y h??m nay s??? ???????c coi l?? n??m sau {year+1}", reply_markup=InlineKeyboardMarkup(button))

            elif data.startswith("schconfirm"):
                none, date = data.split("_")
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
                local_dt = IST.localize(date, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc).replace(tzinfo=None)
                job_id=f"{query.message.chat.id}_{query.message.message_id}"
                Config.SCHEDULE_LIST.append({"job_id":job_id, "date":utc_dt})
                Config.SCHEDULE_LIST = sorted(Config.SCHEDULE_LIST, key=lambda k: k['date'])
                await schedule_a_play(job_id, utc_dt)
                await query.message.edit(f"Succesfully scheduled to stream on <code> {date.strftime('%b %d %Y, %I:%M %p')} </code>")
                await delete_messages([query.message, query.message.reply_to_message])
                
            elif query.data == 'schcancelall':
                await cancel_all_schedules()
                await query.message.edit("T???t c??? c??c Lu???ng ???? l??n l???ch ???? b??? h???y th??nh c??ng.")

            elif query.data == "schcancel":
                buttons = [
                    [
                        InlineKeyboardButton('Yes, Iam Sure!!', callback_data='schcancelall'),
                        InlineKeyboardButton('No', callback_data='schclose'),
                    ]
                ]
                await query.message.edit("B???n c?? ch???c ch???n mu???n h???y t???t c??? c??c lu???ng ???? l??n l???ch kh??ng?", reply_markup=InlineKeyboardMarkup(buttons))
            elif data == "schclose":
                await query.answer("Menu Closed")
                await query.message.delete()
                await query.message.reply_to_message.delete()

        elif query.data == "shuffle":
            if not Config.playlist:
                await query.answer("Playlist is empty.", show_alert=True)
                return
            await shuffle_playlist()
            await query.answer("Playlist shuffled.")
            await sleep(1)        
            await query.message.edit_reply_markup(reply_markup=await get_buttons())
    

        elif query.data.lower() == "pause":
            if Config.PAUSE:
                await query.answer("Already Paused", show_alert=True)
            else:
                await pause()
                await query.answer("Stream Paused")
                await sleep(1)

            await query.message.edit_reply_markup(reply_markup=await get_buttons())
 
        
        elif query.data.lower() == "resume":   
            if not Config.PAUSE:
                await query.answer("Kh??ng c?? g?? b??? T???m d???ng ????? ti???p t???c", show_alert=True)
            else:
                await resume()
                await query.answer("Redumed the stream")
                await sleep(1)
            await query.message.edit_reply_markup(reply_markup=await get_buttons())
          
        elif query.data=="skip": 
            if not Config.playlist:
                await query.answer("No songs in playlist", show_alert=True)
            else:
                await query.answer("Trying to skip from playlist.")
                await skip()
                await sleep(1)
            if Config.playlist:
                title=f"<b>{Config.playlist[0][1]}</b>\n?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????"
            elif Config.STREAM_LINK:
                title=f"<b>Stream Using [Url]({Config.DATA['FILE_DATA']['file']})</b>???  ????????????????????????????????????????????????????????????????????????????????????????????????????????????"
            else:
                title=f"<b>Streaming Startup [stream]({Config.STREAM_URL})</b> ??? ???  ?????????????????????????????????????????????????????????"
            await query.message.edit(f"<b>{title}</b>",
                disable_web_page_preview=True,
                reply_markup=await get_buttons()
            )

        elif query.data=="replay":
            if not Config.playlist:
                await query.answer("No songs in playlist", show_alert=True)
            else:
                await query.answer("trying to restart player")
                await restart_playout()
                await sleep(1)
            await query.message.edit_reply_markup(reply_markup=await get_buttons())


        elif query.data.lower() == "mute":
            if Config.MUTED:
                await unmute()
                await query.answer("Lu???ng kh??ng b??? t???t ti???ng")
            else:
                await mute()
                await query.answer("Lu???ng b??? t???t ti???ng")
            await sleep(1)
            await query.message.edit_reply_markup(reply_markup=await volume_buttons())

        elif query.data.lower() == 'seek':
            if not Config.CALL_STATUS:
                return await query.answer("Not Playing anything.", show_alert=True)
            #if not (Config.playlist or Config.STREAM_LINK):
                #return await query.answer("Startup stream cant be seeked.", show_alert=True)
            await query.answer("trying to seek.")
            data=Config.DATA.get('FILE_DATA')
            if not data.get('dur', 0) or \
                data.get('dur') == 0:
                return await query.answer("????y l?? m???t lu???ng tr???c ti???p v?? kh??ng th??? t??m th???y ???????c.", show_alert=True)
            k, reply = await seek_file(10)
            if k == False:
                return await query.answer(reply, show_alert=True)
            await query.message.edit_reply_markup(reply_markup=await get_buttons())

        elif query.data.lower() == 'rewind':
            if not Config.CALL_STATUS:
                return await query.answer("Kh??ng ch??i g?? c???.", show_alert=True)
            #if not (Config.playlist or Config.STREAM_LINK):
                #return await query.answer("Startup stream cant be seeked.", show_alert=True)
            await query.answer("trying to rewind.")
            data=Config.DATA.get('FILE_DATA')
            if not data.get('dur', 0) or \
                data.get('dur') == 0:
                return await query.answer("This is a live stream and cannot be seeked.", show_alert=True)
            k, reply = await seek_file(-10)
            if k == False:
                return await query.answer(reply, show_alert=True)
            await query.message.edit_reply_markup(reply_markup=await get_buttons())

    
        elif query.data == 'restart':
            if not Config.CALL_STATUS:
                if not Config.playlist:
                    await query.answer("Tr??nh ph??t tr???ng, b???t ?????u STARTUP_STREAM.")
                else:
                    await query.answer('Ti???p t???c danh s??ch ph??t')
            await query.answer("Restrating the player")
            await restart()
            await query.message.edit(text=await get_playlist_str(), reply_markup=await get_buttons(), disable_web_page_preview=True)

        elif query.data.startswith("volume"):
            me, you = query.data.split("_")  
            if you == "main":
                await query.message.edit_reply_markup(reply_markup=await volume_buttons())
            if you == "add":
                if 190 <= Config.VOLUME <=200:
                    vol=200 
                else:
                    vol=Config.VOLUME+10
                if not (1 <= vol <= 200):
                    return await query.answer("Only 1-200 range accepted.")
                await volume(vol)
                Config.VOLUME=vol
                await query.message.edit_reply_markup(reply_markup=await volume_buttons())
            elif you == "less":
                if 1 <= Config.VOLUME <=10:
                    vol=1
                else:
                    vol=Config.VOLUME-10
                if not (1 <= vol <= 200):
                    return await query.answer("Only 1-200 range accepted.")
                await volume(vol)
                Config.VOLUME=vol
                await query.message.edit_reply_markup(reply_markup=await volume_buttons())
            elif you == "back":
                await query.message.edit_reply_markup(reply_markup=await get_buttons())


        elif query.data in ["is_loop", "is_video", "admin_only", "edit_title", "set_shuffle", "reply_msg", "set_new_chat", "record", "record_video", "record_dim"]:
            if query.data == "is_loop":
                Config.IS_LOOP = set_config(Config.IS_LOOP)
                await query.message.edit_reply_markup(reply_markup=await settings_panel())
  
            elif query.data == "is_video":
                Config.IS_VIDEO = set_config(Config.IS_VIDEO)
                await query.message.edit_reply_markup(reply_markup=await settings_panel())
                data=Config.DATA.get('FILE_DATA')
                if not data \
                    or data.get('dur', 0) == 0:
                    await restart_playout()
                    return
                k, reply = await seek_file(0)
                if k == False:
                    await restart_playout()

            elif query.data == "admin_only":
                Config.ADMIN_ONLY = set_config(Config.ADMIN_ONLY)
                await query.message.edit_reply_markup(reply_markup=await settings_panel())
        
            elif query.data == "edit_title":
                Config.EDIT_TITLE = set_config(Config.EDIT_TITLE)
                await query.message.edit_reply_markup(reply_markup=await settings_panel())
        
            elif query.data == "set_shuffle":
                Config.SHUFFLE = set_config(Config.SHUFFLE)
                await query.message.edit_reply_markup(reply_markup=await settings_panel())
        
            elif query.data == "reply_msg":
                Config.REPLY_PM = set_config(Config.REPLY_PM)
                await query.message.edit_reply_markup(reply_markup=await settings_panel())
        
            elif query.data == "record_dim":
                if not Config.IS_VIDEO_RECORD:
                    return await query.answer("This cant be used for audio recordings")
                Config.PORTRAIT=set_config(Config.PORTRAIT)
                await query.message.edit_reply_markup(reply_markup=(await recorder_settings()))
            elif query.data == 'record_video':
                Config.IS_VIDEO_RECORD=set_config(Config.IS_VIDEO_RECORD)
                await query.message.edit_reply_markup(reply_markup=(await recorder_settings()))

            elif query.data == 'record':
                if Config.IS_RECORDING:
                    k, msg = await stop_recording()
                    if k == False:
                        await query.answer(msg, show_alert=True)
                    else:
                        await query.answer("Recording Stopped")
                else:
                    k, msg = await start_record_stream()
                    if k == False:
                        await query.answer(msg, show_alert=True)
                    else:
                        await query.answer("Recording started")
                await query.message.edit_reply_markup(reply_markup=(await recorder_settings()))

            elif query.data == "set_new_chat":
                if query.from_user is None:
                    return await query.answer("B???n kh??ng th??? l???p l???ch ??? ????y, v?? b???n l?? qu???n tr??? vi??n ???n danh. L??n l???ch t??? cu???c tr?? chuy???n ri??ng t??.", show_alert=True)
                if query.from_user.id in Config.SUDO:
                    await query.answer("Thi???t l???p CHAT m???i")
                    chat=query.message.chat.id
                    if Config.IS_RECORDING:
                        await stop_recording()
                    await cancel_all_schedules()
                    await leave_call()
                    Config.CHAT=chat
                    Config.ADMIN_CACHE=False
                    await restart()
                    await query.message.edit("???? thay ?????i th??nh c??ng cu???c tr?? chuy???n")
                    await sync_to_db()
                else:
                    await query.answer("??i???u n??y ch??? c?? th??? ???????c s??? d???ng b???i ng?????i d??ng SUDO", show_alert=True)
            if not Config.DATABASE_URI:
                await query.answer("Kh??ng t??m th???y DATABASE, nh???ng thay ?????i n??y ???????c l??u t???m th???i v?? s??? ???????c ho??n nguy??n khi kh???i ?????ng l???i. Th??m MongoDb ????? l??m cho ??i???u n??y v??nh vi???n.")
        elif query.data.startswith("close"):
            if "sudo" in query.data:
                if query.from_user.id in Config.SUDO:
                    await query.message.delete()
                else:
                    await query.answer("??i???u n??y ch??? c?? th??? ???????c s??? d???ng b???i ng?????i d??ng SUDO", show_alert=True)  
            else:
                if query.message.chat.type != "private" and query.message.reply_to_message:
                    if query.message.reply_to_message.from_user is None:
                        pass
                    elif query.from_user.id != query.message.reply_to_message.from_user.id:
                        return await query.answer("Okda", show_alert=True)
                elif query.from_user.id in Config.ADMINS:
                    pass
                else:
                    return await query.answer("Okda", show_alert=True)
                await query.answer("Menu Closed")
                await query.message.delete()
        await query.answer()
