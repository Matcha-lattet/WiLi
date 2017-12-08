# -*- coding: utf-8 -*-

import numpy as np
import cv2
import urllib.request
import os

#WIN_W=480
#WIN_H=260
WIN_W=1280
WIN_H=960

# gg*:googleMap,  other:cyberjapandata:国土地理院 
map_type_name = ["gghybrid","ggsatellite","ggroadmap", "std","ort_old10","gazo1","seamlessphoto"]
TILE_W = [640,640,640,256,256,256,256]
TILE_H = [640,640,640,256,256,256,256]
min_zoom=[ 0, 0, 0, 2,10,10, 2]
max_zoom=[21,21,21,18,17,17,18]
fmt=["png","png","png", "png", "png","jpg","jpg"]

#テーブル定義を変更することで色々な地図が見れる
##ort:2007-, airphoto:2004-, gazo4:1988-1990, gazo3:1984-1986, gazo2:1979-1983, gazo1:1974-1978
##ort_old10:1961-1964, ort_USA10:1945-1950
#map_type_name = ["ort","airphoto","gazo4","gazo3","gazo2","gazo1","ort_old10","ort_USA10"]
#TILE_W = [256,256,256,256,256,256,256,256]
#TILE_H = [256,256,256,256,256,256,256,256]
#min_zoom=[14, 5,10,10,10,10,10,10]
#max_zoom=[18,18,17,17,17,17,17,17]
#fmt=["jpg","png","jpg","jpg","jpg","jpg","png","png"]

#東京駅
HOME_LON=139.767052
HOME_LAT= 35.681167
HOME_ZOOM=18

TILES_DIR="maptiles/"

max_pixels= [256*2**zm for zm in range(22)]

#開いたタイルへの参照を保存しておく辞書。マップタイプ、ズーム、インデクスx、インデクスyをキーとする
opened_tiles={}
white_tiles={}

#lon:経度, lat:緯度
def ll2pix(lon, lat, zoom):
    pix_x=2**(zoom+7)*(lon/180+1)
    pix_y=2**(zoom+7)*(-np.arctanh(np.sin(np.pi/180*lat))/np.pi+1)
    return pix_x,pix_y

def pix2ll(x,y,zoom):
    lon=180*(x/(2**(zoom+7))-1)
    lat=180/np.pi*(np.arcsin(np.tanh(-np.pi/(2**(zoom+7))*y+np.pi)))
    return lon, lat

#経度・緯度からdx,dyピクセル移動したさいの経度・緯度を返す
def new_ll(lon_cur,lat_cur,zm, dx,dy):
    x,y=ll2pix(lon_cur,lat_cur,zm)
    return pix2ll(x+dx,y+dy,zm)

def dddmm2f(dddmm_mmmm):
    #12345.6789 -> 123度45.6789分 -> 123度.(45.6789/60)
    ddd=int(dddmm_mmmm)//100
    mm_mmmm=dddmm_mmmm-ddd*100
    return ddd+mm_mmmm/60

#タイルを連結して表示ウインドウより大きな画像をつくり、最後にウィンドウサイズにカットして返す
def load_win_img(mtype, lon,lat,zm):
    cx,cy=ll2pix(lon,lat,zm)

    win_left=int(cx-WIN_W/2)
    win_top=int(cy-WIN_H/2)

    x_nth=win_left//TILE_W[mtype]
    y_nth=win_top//TILE_H[mtype]

    left_offset = win_left%TILE_W[mtype]
    top_offset = win_top%TILE_H[mtype]

    vcon_list=[]
    tot_height=0
    tot_height += TILE_H[mtype]-top_offset
    j=0
    while True:
        hcon_list=[]
        tot_width=0
        tot_width += TILE_W[mtype]-left_offset
        i=0
        while True:
            img_tmp=open_tile_img(mtype, x_nth+i,y_nth+j,zm)
            hcon_list.append(img_tmp) #
            if tot_width >= WIN_W:
                break
            tot_width += TILE_W[mtype]
            i+=1
        hcon_img=cv2.hconcat(hcon_list)
        vcon_list.append(hcon_img)
        if tot_height >= WIN_H:
            break
        tot_height += TILE_H[mtype]
        j+=1
    convined_img=cv2.vconcat(vcon_list)

    return convined_img[top_offset:top_offset+WIN_H, left_offset:left_offset+WIN_W, :]

def tile_file_name(mtype, x_nth,y_nth,zm):
#    x_nth=x//TILE_W[mtype]
#    y_nth=y//TILE_H[mtype]
    return TILES_DIR+"z%02d/%s_z%02d_%dx%d_%07d_%07d"%(zm,map_type_name[mtype],zm,TILE_W[mtype],TILE_H[mtype],x_nth,y_nth)+"."+fmt[mtype]

#タイルを開く
#まだ1回も開いたことがない地点 -> ダウンロード・保存を試みる。失敗したら白塗りの画像を返す。成功したら地点・ズーム・マップタイプを辞書に登録して、以後、開き済みとする
#ファイルに保存してあるが、開いていない　-> 普通に開く。辞書への登録もする
#すでに開いている -> 辞書に登録されている画像を返す
def open_tile_img(mtype, x_nth,y_nth,zm):
    if (mtype, zm,x_nth,y_nth) in opened_tiles:
        print("opened_tiles(%d,%d,%d,%d)"%(mtype, zm,x_nth,y_nth))
        return opened_tiles[(mtype, zm,x_nth,y_nth)]

    fname=tile_file_name(mtype, x_nth,y_nth,zm)
    if os.path.exists(fname):
        print("opening tile(%d,%d,%d,%d)"%(mtype,zm,x_nth,y_nth) +" -> "+fname)
    else:
        c_lon,c_lat=pix2ll((x_nth+0.5)*TILE_W[mtype],(y_nth+0.5)*TILE_H[mtype],zm)
        if map_type_name[mtype][0:2]=="gg":
            url="http://maps.google.com/maps/api/staticmap?"
            url+="&center=%.08f,%08f&zoom=%d&size=%dx%d&maptype=%s" % \
            (c_lat,c_lon,zm,TILE_W[mtype],TILE_H[mtype],map_type_name[mtype][2:])
        #maptype
        #roadmap     通常の地図。maptypeパラメータのデフォルトの値
        #satellite   航空写真
        #terrain     地形や植生を表示する、物理的な地形地図画像
        #hybrid      航空写真＋通常の地図。主要道路と地名を航空写真の上にレイヤー表示
        else:
            url="http://cyberjapandata.gsi.go.jp/xyz/%s/%d/%d/%d.%s"%(map_type_name[mtype],zm,x_nth,y_nth,fmt[mtype])
        print("Downloading... ")
        print(url)
        print(" -> "+fname)
        try:
            urllib.request.urlretrieve(url,fname) #python3
#            urllib.urlretrieve(url,fname) #python2
        except Exception as e:
            #タイルを取得できなかったら白く塗りつぶした画像を返す
            print(e)
            print("Download faild -> blank")
            if (TILE_W[mtype],TILE_H[mtype]) in white_tiles:
                return white_tiles[(TILE_W[mtype],TILE_H[mtype])]
            else:
                white=np.zeros([TILE_H[mtype],TILE_W[mtype],3],dtype=np.uint8)
                white[:,:,:]=255
                white_tiles[(TILE_W[mtype],TILE_H[mtype])]=white
                return white
    opened_tiles[(mtype, zm,x_nth,y_nth)]=cv2.imread(fname)
    return opened_tiles[(mtype, zm,x_nth,y_nth)]


if __name__ == '__main__':
    map_type=0
    c_lon=HOME_LON
    c_lat=HOME_LAT
    zoom=HOME_ZOOM
    cv2.namedWindow("Ackerman's Map", cv2.WINDOW_AUTOSIZE)

    map_type_bak = -1
    c_lon_bak = -1
    c_lat_bak = -1
    zoom_bak = -1

    #mainloop
    while (True):
        if map_type_bak != map_type or c_lon_bak != c_lon or c_lat_bak != c_lat or zoom_bak != zoom:
            win_img=load_win_img(map_type, c_lon,c_lat,zoom)
            cv2.imshow("Ackerman's Map", win_img)
        map_type_bak = map_type
        c_lon_bak = c_lon
        c_lat_bak = c_lat
        zoom_bak = zoom

        k=cv2.waitKey(0) & 0xff  #GPS機能追加時には待ち時間を0にせずポーリング
        print("pressed:"+str(k))
        if k == ord('+'):
            if zoom<max_zoom[map_type]: 
                zoom += 1
        elif k == ord('-'):
            if zoom>min_zoom[map_type]: 
                zoom -= 1
        elif k == ord('a'):
            c_lon,c_lat=new_ll(c_lon,c_lat,zoom,-WIN_W/4,0)
        elif k == ord('s'):
            c_lon,c_lat=new_ll(c_lon,c_lat,zoom,0,-WIN_H/4)
        elif k == ord('d'):
            c_lon,c_lat=new_ll(c_lon,c_lat,zoom,0,+WIN_H/4)
        elif k == ord('f'):
            c_lon,c_lat=new_ll(c_lon,c_lat,zoom,+WIN_W/4,0)
        elif k == 32:
            #space key
            map_type = (map_type+1)%len(map_type_name)
            if zoom > max_zoom[map_type]:
                zoom=max_zoom[map_type]
            if zoom < min_zoom[map_type]:
                zoom=min_zoom[map_type]
        elif k == 8:
            #Backspace
            map_type = (map_type-1)%len(map_type_name)
            if zoom > max_zoom[map_type]:
                zoom=max_zoom[map_type]
            if zoom < min_zoom[map_type]:
                zoom=min_zoom[map_type]
        elif k == ord("q"):
            break
    cv2.destroyAllWindows()