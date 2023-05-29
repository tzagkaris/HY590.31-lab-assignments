

![image-20230515184151071](/home/spiros/snap/typora/78/.config/Typora/typora-user-images/image-20230515184151071.png)

>  Image X: proxy.py running on the rasberry pi

The traffic between the rasberry pi and the server is not ssl encrypted. A man-in-the-middle attack easily captures the communication between the devices. Similar attacks can also alter our messages, making our communication unreliable and or data security non existent. 

 If our server is hooked with a database, then our database is at major risk as bad actors can flood it with fake data.

 Regarding security concerns of our data what we thought about is that a bad actor can analyze such data in order to predict apartment presence and thus plan physical theft.



---

![image-20230515200424331](/home/spiros/snap/typora/78/.config/Typora/typora-user-images/image-20230515200424331.png)

> Image X+1: Adding the time field on the request and inspecting the request using the proxy.

 If the timestamps differ a lot then the information stored on the database will not be accurate. Times could overlap or be out of order making them invalid and/or hard to analyze in real-time. If our cloud server ran logic and had the ability to configure devices ( such as changing thresholds ) then this setup would not be reliable.    