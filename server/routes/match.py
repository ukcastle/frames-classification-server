from datetime import datetime, timedelta
from flask import request, Blueprint
from server.tools.face_tool import FaceTool

from server.db.db import  DB

from server.store.checklistStore import Checklist, MemberDict

from server.tools.mask_detector import MaskDetector

import numpy as np
import cv2

ft = FaceTool()
md = MaskDetector('server/tools/mask_detector.model')
bp = Blueprint('match', __name__, url_prefix='/match')

checkStack = {
    # fNum+state : count
}

@bp.route('/', methods=['POST'], strict_slashes=False)
def match():

    db = DB.instance()
    result = []

    nparr = np.fromstring(request.files['face'].read(), np.uint8)
    face = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    tp = request.form["temperature"]
    fNum = request.form["facilityNum"]
    state = request.form["state"]

    if md.isMasked(face):
        result.append(True)
        result.append("")

    else:
        landmark = ft.feature(face)

        data, distance = ft.match(landmark)
        print(f"distance: {distance}")

        name = data["name"]
        mno = data["mno"]

        result.append(False) # masked
        result.append(name) # name
        if checkStack.get(f'{fNum}{state}') is None:
            checkStack[f'{fNum}{state}']["val"] = 1
            checkStack[f'{fNum}{state}']["mno"] = mno
        else:
            if checkStack[f'{fNum}{state}']["mno"] == mno:
                checkStack[f'{fNum}{state}']["val"] += 1
            else:
                del checkStack[f'{fNum}{state}']

        if checkStack.get(f'{fNum}{state}') is None and checkStack[f'{fNum}{state}']["val"] >= 3:
            del checkStack[f'{fNum}{state}']
            result.append(True) # display
        else:
            result.append(False) # display

        checklist: MemberDict = Checklist.instance()
        checklist.check(memberNum=mno, ifNotExists=lambda: db.status.insertStatus(state=state, facilityNum=fNum, memberNum=mno, temperature=tp, regdate=datetime.now() + timedelta(seconds=10)),ifExists=None)

        print(f"tp = {tp}, fNum = {fNum}, state = {state}, name = {name}")

    return {'data': result}, 200 # 데이터 반환하는거 협의 필요함 지금은 상태 + name