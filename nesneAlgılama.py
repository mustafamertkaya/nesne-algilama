import cv2
import numpy as np
import time


whT = 320
cap = cv2.VideoCapture(0)

classFile="obj.names"
classNames=[]
with open(classFile,"rt") as f:
    classNames=f.read().rstrip("\n").split("\n")


colors = np.random.uniform(0, 255, size=(len(classNames), 3)) #rastgele renk
# FPS başlatma
font = cv2.FONT_HERSHEY_PLAIN #Yazı tipi
starting_time = time.time()
frame_id = 0

#model alma
modelcfg="yolov4-obj.cfg"
modelWeights="yolov4-obj_last.weights"
model=cv2.dnn.readNetFromDarknet(modelcfg ,modelWeights)


def findObject(detectionLayers,img):
    hT,wT,cT=img.shape
    bbox=[] #sınırlayıcı kutularımızı tutan liste
    classIds=[] #sınıflarımızı tutan id listesi
    confs=[] #Bulunan nesnelerin güven değerini tutan listemiz
    
    # bütün resim dolasarak güven skorları sınırlar belirlenir ve bulunan nesnelerin ne olduğu belirlenir.
    for detectionLayer in detectionLayers: # Bütün output layers tek tek gezer
        for objectDetection in detectionLayer: # Herbir output layers içini taramak için
            scores=objectDetection[5:]  
            classId=np.argmax(scores)  
            confidence=scores[classId] 
            if confidence>0.2: 
                w,h=int(objectDetection[2]*wT),int(objectDetection[3]*hT)
                x,y=int((objectDetection[0]*wT)-w/2),int((objectDetection[1]*hT)-h/2)
                bbox.append([x,y,w,h])
                classIds.append(classId)
                confs.append(float(confidence))

    #Non maxiumum suppression ; Güven skoruna göre atılacaklar atılır
    indices=cv2.dnn.NMSBoxes(bbox,confs,0.8,0.3)

    # belirlenen güven skorlarında en iyisi için kutu çizdirilir.
    for i in range(len(bbox)):
        if i in indices:
            box=bbox[i]
            x,y,w,h=box[0],box[1],box[2],box[3] 
            label = str(classNames[classIds[i]])
            confidence = confs[i]
            color = colors[classIds[i]]
            cv2.rectangle(img,(x,y),(x+w,y+w),color,3)
            cv2.putText(img, f'{classNames[classIds[i]].upper()} {int(confs[i] * 100)}%',
                   (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
       
       

while True:
    success,img=cap.read()
    frame_id += 1
    blob=cv2.dnn.blobFromImage(img,1/255,(whT,whT),[0,0,0],1,crop=False) # görüntüyü belirli standartlara sınırlıyor

    model.setInput(blob) # model veriyi göderme

    layerNames=model.getLayerNames()
    outputLayers=[layerNames[i-1] for i in model.getUnconnectedOutLayers()]

    detectionLayers=model.forward(outputLayers) # modele gönderilen verinin sonucu
    findObject(detectionLayers,img) # fonksiyonu çalıştırma

   # FPS bitiş
    elapsed_time = time.time() - starting_time
    fps = frame_id / elapsed_time
    cv2.putText(img, "FPS: " + str(round(fps, 2)), (10, 50), font, 4, (0, 0, 0), 3)


    cv2.imshow("Nesne Algilama",img)
    k = cv2.waitKey(20) & 0xFF
    if k == 27:
        break
    cv2.waitKey(50)