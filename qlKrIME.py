# author javalia
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# 이 프로그램은 GPL라이센스를 따릅니다.


import minqlx
import re
import copy

"""
기존에 작성한 소스모드 플러그인을 다른 언어와 환경으로 이식했다.
이렇게 리스트 안의 리스트를 쓰지 않고 쪼갠 것은 파이썬을 활용하기가 힘들어서다.
이 주석을 다는 시점에서 파이썬을 배운 지 이틀째. 이 프로그램을 만들기 시작한지 이틀 째
"""

"""
ㄱ ㄲ ㄴ ㄷ ㄸ ㄹ ㅁ ㅂ ㅃ ㅅ ㅆ ㅇ ㅈ ㅉ ㅊ ㅋ ㅌ ㅍ ㅎ
r R s e E f a q Q t T d w W c z x v h
"""
FIRST_SYLLABLE = (0x3131, 0x3132, 0x3134, 0x3137, 0x3138, 0x3139, 0x3141, 0x3142, 0x3143, 0x3145,
    0x3146, 0x3147, 0x3148, 0x3149, 0x314a, 0x314b, 0x314c, 0x314d, 0x314e
)

"""
ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ
/k o i O j p u P h hk ho hl y n nj np nl b m ml l
"""
SECOND_SYLLABLE = (0x314f, 0x3150, 0x3151, 0x3152, 0x3153, 0x3154, 0x3155, 0x3156, 0x3157, 0x3158,
    0x3159, 0x315a, 0x315b, 0x315c, 0x315d, 0x315e, 0x315f, 0x3160, 0x3161, 0x3162,
    0x3163)

"""
\0 ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ
\0 r R rt s sw sg e f fr fa fq ft fx fv fg a q qt t T d w c z x v g
"""
LAST_SYLLABLE = (0x0000, 0x3131, 0x3132, 0x3133, 0x3134, 0x3135, 0x3136, 0x3137, 0x3139, 0x313a,
    0x313b, 0x313c, 0x313d, 0x313e, 0x313f, 0x3140, 0x3141, 0x3142, 0x3144, 0x3145,
    0x3146, 0x3147, 0x3148, 0x314a, 0x314b, 0x314c, 0x314d, 0x314e)

FIRST_SYLLABLE_ENGLISH_TYPE = (
    "r", "R", "s,S", "e", "E", "f,F", "a,A", "q", "Q", "t", "T", "d,D", "w", "W", "c,C", "z,Z", "x,X",
    "v,V", "g,G"
)

SECOND_SYLLABLE_ENGLISH_TYPE = (
    "k,K", "o", "i,I", "O", "j,J", "p", "u,U", "P", "h,H", "hk,HK,Hk,hK", "ho,HO,Ho", "hl,HL,Hl,hL", "y,Y", "n,N", "nj,NJ,Nj,nJ",
        "np,Np,", "nl,NL,Nl,nL", "b,B", "m,M", "ml,ML,Ml,mL", "l,L", ""
)

LAST_SYLLABLE_ENGLISH_TYPE = (
    "", "r", "R", "rt", "s,S", "sw,Sw", "sg,SG,Sg,sG", "e", "f,F", "fr,Fr", "fa,FA,Fa,fA", "fq,Fq", "ft,Ft",
    "fx,FX,Fx,fX", "fv,FV,Fv,fV", "fg,FG,Fg,fG", "a,A", "q", "qt", "t", "T", "d,D", "w", "c,C", "z,Z", "x,X", "v,V", "g,G", ""
)

CHAT_MAXLENGTH = 256

ENCODE_EMPTY = 0
ENCODE_FIRST = 1
ENCODE_SECOND = 2
ENCODE_LAST = 3

def getFirstSyllabelIndex(string):
    for i, part in enumerate(FIRST_SYLLABLE_ENGLISH_TYPE) :
        for n in part.rsplit(","):
            if n == string:
                return i
    return -1

def getSecondSyllabelIndex(string):
    for i, part in enumerate(SECOND_SYLLABLE_ENGLISH_TYPE) :
        for n in part.rsplit(","):
            if n == string:
                return i
    return -1

def getLastSyllabelIndex(string):
    for i, part in enumerate(LAST_SYLLABLE_ENGLISH_TYPE):
        for n in part.rsplit(","):
            if n == string:
                return i
    return -1

def encodecharacter(first, second, last):

    bitpattern = 0
    utf8buffer = ""

    if first != "":

        if second != "":

            lastindex = getLastSyllabelIndex(last)
            bitpattern = 0xAC00 + ((getFirstSyllabelIndex(first) * 21 + getSecondSyllabelIndex(second)) * 28)  + (lastindex if lastindex != -1 else 0)

        else:

            bitpattern = FIRST_SYLLABLE[getFirstSyllabelIndex(first)]

    else:

        if second != "":
            bitpattern = SECOND_SYLLABLE[getSecondSyllabelIndex(second)]

        elif last != "":
            bitpattern = LAST_SYLLABLE[getLastSyllabelIndex(last)]

    if bitpattern != 0:

        character = bytearray(3)
        character[0] = (0xE0 | ((bitpattern & 0xffff) >> 12))
        character[1] = (0x80 | ((bitpattern & 0xfff) >> 6))
        character[2] = (0x80 | (bitpattern & 0x003f))
        utf8buffer += bytearray.decode(character)
        return utf8buffer

    else:

        return utf8buffer


class qlKrIME(minqlx.Plugin):

    def __init__(self):
        super().__init__()
        self.add_hook("client_command", self.handle_client_command, priority=minqlx.PRI_HIGH)
        self.set_cvar_once("qlx_KrIME_Version", "1.0.0.0")
        self.set_cvar_once("qlx_KrIME_Trigger", "[,]")
        self.set_cvar_limit_once("qlx_KrIME_ClientTrigger", "1", "0", "1")
        self.cmdbuffer = [[] for i in range(65)]#for 64 people server.

    def handle_client_command(self, player, cmd):

        # 명령어 중복 해석을 막음. 수행시간은 정상적인 경우 O(1)
        if cmd in self.cmdbuffer[player.id]:
            self.cmdbuffer[player.id].remove(cmd)
            return

        trigger = self.get_cvar("qlx_KrIME_Trigger")

        if self.get_cvar("qlx_KrIME_ClientTrigger") == 0 or trigger == "":
            return

        cmdpattern = re.compile("say\s+|say_team\s+", re.IGNORECASE)
        matchresult = cmdpattern.match(cmd)

        if matchresult is None:
            return
        else:

            cmdhead = matchresult.group(0)
            text = cmdpattern.sub("", cmd, 1)
            text = text.rstrip()
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            elif text.startswith("'") and text.endswith("'"):
                text = text[1:-1]

            triggerpattern = re.compile(trigger)
            triggermatchresult = triggerpattern.match(text)

            if triggermatchresult is None:
                return
            else:
                text = triggerpattern.sub("", text, 1)

            encodestatus = ENCODE_EMPTY
            first = ""
            second = ""
            last = ""
            resulttext = ""
            rtlength = 0

            for c in text:
                temp = copy.deepcopy(c)

                if encodestatus == ENCODE_EMPTY:

                    # 초성 중성 종성 아무 것도 없다.
                    # 한 글자가 입력될 경우 자모는 모두 초성이거나 중성이어야 한다.
                    if getFirstSyllabelIndex(temp) != -1:
                        first = temp
                        encodestatus = ENCODE_FIRST

                    elif getSecondSyllabelIndex(temp) != -1:
                        second = temp
                        encodestatus = ENCODE_SECOND

                    else:
                        if rtlength + 1 < CHAT_MAXLENGTH:
                            resulttext += temp


                elif encodestatus == ENCODE_FIRST:

                    # 초성이 1개 입력되었으므로 앞으로의 가능성은 다른 초성이 들어오고 그것이 현재 있는
                    # 초성과 합쳐지는 것이 가능해 종성으로 변하는 경우
                    # 다른 중성이 들어와 그것이 현재 있는 초성에 이어지는 경우
                    # 그 이외의 문자가 들어와 조합이 중단될 경우
                    if getFirstSyllabelIndex(temp) != -1:

                        temp2 = first + temp
                        if getLastSyllabelIndex(temp2) != -1:
                            first = ""
                            last = temp2
                            encodestatus = ENCODE_LAST
                        else:
                            if rtlength + 3 < CHAT_MAXLENGTH:
                                resulttext += encodecharacter(first, second, last)
                            first = temp
                            encodestatus = ENCODE_FIRST
                    elif getSecondSyllabelIndex(temp) != -1:

                        second = temp
                        encodestatus = ENCODE_SECOND
                    else:
                        # 초성이 입력된 상태로 한글이 아닌 다른 문자가 들어왔다. 완성된 글자를 내보낸다.

                        if rtlength + 3 < CHAT_MAXLENGTH:
                            resulttext += encodecharacter(first, second, last)
                        first = ""
                        encodestatus = ENCODE_EMPTY
                        resulttext += temp

                elif encodestatus == ENCODE_SECOND:

                    # 초성과 중성이 모두 있거나, 중성만 있다.
                    if getLastSyllabelIndex(temp) != -1:

                        # 종성을 받아들일 수 있다.
                        if first != "":
                            last = temp
                            encodestatus = ENCODE_LAST
                        else:  # 초성없이 종성이 되는 초성을 받은 상태. 현재 글자를 내보낸다.
                            if rtlength + 3 < CHAT_MAXLENGTH:
                                resulttext += encodecharacter(first, second, last)
                            first = temp
                            second = ""
                            last = ""
                            encodestatus = ENCODE_FIRST

                    elif getFirstSyllabelIndex(temp) != -1:

                        # 종성이 될 수 없는 초성 입력이 들어왔다. 이것이 가능한가?
                        if rtlength + 3 < CHAT_MAXLENGTH:
                            resulttext += encodecharacter(first, second, last)
                        first = temp
                        second = ""
                        last = ""
                        encodestatus = ENCODE_FIRST

                    elif getSecondSyllabelIndex(temp) != -1:

                        if len(second) == 2:
                            # 중성이 들어왔지만 받아들일 수 없으므로 내보낸다.
                            if rtlength + 3 < CHAT_MAXLENGTH:
                                resulttext += encodecharacter(first, second, last)
                            first = ""
                            second = temp
                        else:
                            temp2 = second + temp
                            if getSecondSyllabelIndex(temp2) != -1:
                                second += temp
                            else:
                                if rtlength + 3 < CHAT_MAXLENGTH:
                                    resulttext += encodecharacter(first, second, last)
                                first = ""
                                second = temp

                    else:
                        # 중성이 입력된 상태로 한글이 아닌 다른 문자가 들어왔다. 완성된 글자를 내보낸다.
                        if rtlength + 3 < CHAT_MAXLENGTH:
                            resulttext += encodecharacter(first, second, last)
                        first = ""
                        second = ""
                        last = ""
                        encodestatus = ENCODE_EMPTY
                        if rtlength + 1 < CHAT_MAXLENGTH:
                            resulttext += temp

                elif encodestatus == ENCODE_LAST:

                    # 초성, 중성, 종성이 모두 있거나 종성만 있는 상태

                    # 종성이 온다면 기존 종성과 조합 가능한지 확인
                    if getLastSyllabelIndex(temp) != -1:

                        if len(last) == 2:  # 종성이 이미 2개인 상태
                            if rtlength + 3 < CHAT_MAXLENGTH:
                                resulttext += encodecharacter(first, second, last)
                            first = temp
                            second = ""
                            last = ""
                            encodestatus = ENCODE_FIRST

                        else:

                            temp2 = last + temp

                            if getLastSyllabelIndex(temp2) != -1:

                                last = temp2

                            else:  # 종성이 이미 있는데 조합될 수 없는 종성이 왔다.

                                if rtlength + 3 < CHAT_MAXLENGTH:
                                    resulttext += encodecharacter(first, second, last)
                                first = temp  # 모든 단일 종성은 초성이 될 수 있다.
                                second = ""
                                last = ""
                                encodestatus = ENCODE_FIRST

                    elif getFirstSyllabelIndex(temp) != -1:

                        # 종성까지 입력되었는데 초성이 왔다.
                        if rtlength + 3 < CHAT_MAXLENGTH:
                            resulttext += encodecharacter(first, second, last)
                        first = temp
                        second = ""
                        last = ""
                        encodestatus = ENCODE_FIRST

                    elif getSecondSyllabelIndex(temp) != -1:

                        temp2 = ""
                        if len(last) == 2:  # 종성이 있을 때 중성이 입력될 경우 종성을 다음 중성에 떼어주고 자신은 완성된다.
                            temp2 = copy.deepcopy(last[1])
                            last = last[0]
                        else:
                            temp2 = copy.deepcopy(last)
                            last = ""

                        if rtlength + 3 < CHAT_MAXLENGTH:
                            resulttext += encodecharacter(first, second, last)
                        first = temp2
                        second = temp
                        last = ""
                        encodestatus = ENCODE_SECOND

                    else:

                        # 한글 자모가 아닌 문자가 들어왔다.
                        if rtlength + 3 < CHAT_MAXLENGTH:
                            resulttext += encodecharacter(first, second, last)
                        first = ""
                        second = ""
                        last = ""
                        encodestatus = ENCODE_EMPTY
                        if rtlength + 1 < CHAT_MAXLENGTH:
                            resulttext += temp

            # 남은 문자를 기록한다.
            if rtlength + 3 < CHAT_MAXLENGTH:
                resulttext += encodecharacter(first, second, last)

            self.cmdbuffer[player.id].append(cmdhead + resulttext)
            minqlx.client_command(player.id, cmdhead + resulttext)


        return minqlx.RET_STOP_ALL
