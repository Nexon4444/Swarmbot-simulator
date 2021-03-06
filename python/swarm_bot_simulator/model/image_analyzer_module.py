import math
import sys
import threading

import requests
import cv2
import numpy as np
from scipy.spatial import distance
from swarm_bot_simulator.model.algorithm_module import Vector
# from swarm_bot_simulator.model.algorithm import Vector
import imutils
from shapely.geometry import LineString
from queue import LifoQueue

class Detector:
    wait_for_key_press = False
    # wait_for_key_press = True
    show_images = False
    # show_images = True

    def __init__(self, config):
        self.config = config

        if config["camera_settings"]["launch_analysis_windows"] is True:
            Detector.show_images = True
        else:
            Detector.show_images = False
        self.remembered_flag = False
        self.remembered_board = None

    def angle(self, seg1, seg2, dist_point):
        Ax = seg1[0]
        Ay = seg1[1]

        Bx = seg2[0]
        By = seg2[1]

        Cx = dist_point[0]
        Cy = dist_point[1]

        A = Ay-By
        B = Bx-Ax
        C = Ax*By - Ay*Bx

        vec = Vector(A, B)
        vx = vec.x
        vy = vec.y

        k = (A*Cx + B*Cy + C)/(A*vx + B*vy)

        if k >= 0:
            return vec.get_angle()

        else:
            vec_angle = vec.get_angle()
            return (vec_angle + math.pi) % (2*math.pi)

    def rotate(self, origin, point, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """
        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy

    def translate(self, point, translation):
        return (point[0]+translation[0],
                point[1]+translation[1])

    def find_left_up_point(self, box):
        min_dist = sys.maxsize
        left_down = None
        for indx, point in enumerate(box):
            dist = distance.euclidean((0, 0), point)
            if dist < min_dist:
                left_down = point
            min_dist = dist

        return left_down

    def find_left_down_point(self, box, left_up):
        min_x = sys.maxsize
        left_down = None
        for indx, point in enumerate(box):
            if point[0] == left_up[0] and point[1] == left_up[1]:
                continue
            if point[0] < min_x:
                left_down = point
                min_x = point[0]

        return left_down

    def find_center_other_points(self, box, left_up, left_down):
        left_up = left_up.tolist()
        left_down = left_down.tolist()
        box_list = box.tolist()
        box_list.remove(left_up)
        box_list.remove(left_down)

        center = LineString([box_list[0], box_list[1]]).centroid
        return center.x, center.y

    def count_transform(self, board_parameters):
        left_up = self.find_left_up_point(box=board_parameters[2])
        left_down = self.find_left_down_point(box=board_parameters[2], left_up=left_up)
        center_other = self.find_center_other_points(box=board_parameters[2], left_up=left_up, left_down=left_down)
        angle = self.angle(left_up, left_down, center_other) - math.pi/2
        return -left_up[0], -left_up[1], center_other, angle

    def transform(self, point, transformation_params):
        p = self.translate(point, (transformation_params[0], transformation_params[1]))
        p = self.rotate((0, 0), p, transformation_params[3])
        return p

    def remember(self, board_parameters):
        if self.config["camera_settings"]["remember_first"] is True and self.remembered_flag is False:
            self.remembered_board = board_parameters
            self.remembered_flag = True
            return board_parameters
        elif self.config["camera_settings"]["remember_first"] is True and self.remembered_flag is True:
            return self.remembered_board
        else:
            return board_parameters

    def analyze_image(self, img, imgScale):
        # img = cv2.imread(img_path)
        newX, newY = img.shape[1] * imgScale, img.shape[0] * imgScale
        resized = cv2.resize(img, (int(newX), int(newY)))
        # self.show_and_wait(resized, "resized")

        marker = self.filter_marker(resized)
        board = self.filter_board(resized)

        board_parameters = self.find_board_parameters(board, imgScale)
        marker_parameters = self.find_marker_parameters(marker, imgScale)

        board_parameters = self.remember(board_parameters)

        box_transformed, triangle_transformed = self.get_board_marker_translated_positions(board_parameters, marker_parameters)

        box_contour = self.create_contour_from_list(box_transformed)
        triangle_contour = self.create_contour_from_list(triangle_transformed[1])

        board_img = np.zeros((800, 800, 3), np.uint8)
        cv2.drawContours(board_img, [box_contour], 0, (0, 255, 0), 3)
        cv2.drawContours(board_img, [triangle_contour], 0, (0, 0, 255), 3)
        # self.show_and_wait(board_img, "board+marker visualized")
        # print(marker_parameters[1])
        # cv2.imshow("board+marker visualized", board_img)
        return board_parameters, marker_parameters, triangle_transformed

    def create_contour_from_list(self, list_of_points):
        return np.array(list_of_points, dtype=np.int32)

    def get_board_marker_translated_positions(self, board_parameters, marker_parameters):
        box = board_parameters[2]
        box = np.int0(box)
        triangle = marker_parameters[2]
        # print("triangle:\n" + str(triangle))
        triangle = np.int0(triangle)
        trans_params = self.count_transform(board_parameters=board_parameters)
        box_transformed = np.int0([self.transform(point, trans_params) for point in box])

        triangle_transformed = (self.transform(marker_parameters[0], trans_params),
                                np.int0([self.transform(point, trans_params) for point in triangle]),
                                # self.transform(marker_parameters[0], trans_params)
                                )
        # print ("triangle_transformed: \n" + str(triangle_transformed[1]))
        return box_transformed, triangle_transformed

    def show_and_wait(self, image, name):
        # my_var_name = [k for k, v in locals().iteritems() if v == image][0]
        if Detector.show_images:
            cv2.imshow(name, image)
            if Detector.wait_for_key_press:
                cv2.waitKey(0)

    def detect_shape(self, c):
        shape = "unidentified"
        approx = self.approximate(c)

        if len(approx) == 3:
            shape = "triangle"

        elif len(approx) == 4:

            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)

            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
        elif len(approx) == 5:
            shape = "pentagon"


        return shape

    def approximate(self, contour):
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, self.config["camera_settings"]["shape_tolerance"] * peri, True)
        return approx

    def contourize(self, img):
        cnts = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

        cnts = imutils.grab_contours(cnts)
        return cnts

    def find_board_parameters(self, image, ratio):
        cnts = self.contourize(image)
        # cnt_array = np.asarray(cnts)
        areas = dict()

        for indx, c in enumerate(cnts):
            M = cv2.moments(c)
            area = M["m00"]

            if area == 0:
                continue

            shape = self.detect_shape(c)
            if shape == "rectangle":
                areas[indx] = area
                continue

        # print("max: " + str(max(areas, key=areas.get)))
        largest_cont = cnts[max(areas, key=areas.get)]

        board_img = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)
        self.show_and_wait(board_img, "biggest rectangle")
        rect = cv2.minAreaRect(largest_cont)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        rect_par = self.rectangle_params(box)
        rect_par = (int(rect_par[0]), int(rect_par[1]))
        M = cv2.moments(box)
        cX = int((M["m10"] / M["m00"]))
        cY = int((M["m01"] / M["m00"]))
        center = (cX, cY)


        return center, rect_par, box

    def find_marker_parameters(self, image, ratio):
        cnts = self.contourize(image)
        areas = dict()

        triangle = None
        center = None
        for indx, c in enumerate(cnts):

            M = cv2.moments(c)
            area = M["m00"]

            if area == 0:
                continue

            shape = self.detect_shape(c)
            if shape == "triangle":
                areas[indx] = area
                continue

        largest_cont = cnts[max(areas, key=areas.get)]
        M = cv2.moments(largest_cont)
        cX = int((M["m10"] / M["m00"]))
        cY = int((M["m01"] / M["m00"]))
        center = (cX, cY)
        aprox = self.approximate(largest_cont)
        aprox = np.int0(aprox)
        seg1, seg2, seg3 = self.get_oriented_triangle_points(aprox)
        # print(str("segs: ") + str(seg1) +"\n" + str(seg2) + "\n" + str(seg3))
        x = 3

        return center, math.degrees(self.angle(seg1, seg2, seg3)), [el[0] for el in aprox]

    def rectangle_params(self, points):
        # m = MultiPoint(points)
        distances_list = [distance.euclidean(points[0], points[1]),
                          distance.euclidean(points[0], points[2]),
                          distance.euclidean(points[0], points[3])]

        distances_list.remove(max(distances_list))
        return distances_list

    def get_oriented_triangle_points(self, cont):
        # pom = cont[0][0][0]
        p0 = tuple(cont[0][0])
        p1 = tuple(cont[1][0])
        p2 = tuple(cont[2][0])

        d01 = distance.euclidean(p0, p1)
        d12 = distance.euclidean(p1, p2)
        d02 = distance.euclidean(p0, p2)

        dist_dict = {(p0, p1): d01,
                     (p1, p2): d12,
                     (p0, p2): d02}

        # point_dict = {0: (p0, p1),
        #               1: (p1, p2),
        #               2: (p0, p2)}

        sorted_points = sorted(dist_dict.items(), key=lambda kv: kv[1])
        sorted_points.reverse()
        # print(str(sorted_points))
        longer_point1 = sorted_points[0][0][0]
        longer_point2 = sorted_points[0][0][1]
        #
        # print("longer_point1: " + str(longer_point1))
        # print("longer_point2: " + str(longer_point2))

        if p0 is not longer_point1 and p0 is not longer_point2:
            further_point = p0
        elif p1 is not longer_point1 and p1 is not longer_point2:
            further_point = p1
        elif p2 is not longer_point1 and p2 is not longer_point2:
            further_point = p2

        return longer_point1, longer_point2, further_point

    def filter_marker(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_red = np.array([170, 50, 50])
        upper_red = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        lower_red = np.array([0, 50, 50])
        upper_red = np.array([5, 255, 255])

        mask2 = cv2.inRange(hsv, lower_red, upper_red)

        mask = mask1+mask2

        res = cv2.bitwise_and(image, image, mask=mask)

        # cv2.imshow('image', image)
        # cv2.imshow('mask', mask)
        self.show_and_wait(res, "res filtered")
        eroded = cv2.erode(res, None, iterations=2)
        self.show_and_wait(eroded, "marker")
        gray = cv2.cvtColor(eroded, cv2.COLOR_BGR2GRAY)
        return gray

    def filter_board(self, img):
        self.show_and_wait(img, "board-original")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.show_and_wait(gray, "board-gray")

        eroded = cv2.erode(gray, None, iterations=2)
        self.show_and_wait(eroded, "board-eroded")

        blurred = cv2.GaussianBlur(eroded, (5, 5), 0)
        thresh = cv2.threshold(blurred, self.config["camera_settings"]["gray_scale_threshold"], 255, cv2.THRESH_BINARY)[1]
        self.show_and_wait(thresh, "board-thresh")

        return thresh


class VideoAnalyzer:
    def __init__(self, config):
        self.q = LifoQueue()
        self.config = config
        self.photo_url = config["camera_settings"]["photo_url"]
        self.shape_detector = Detector(config)
        self.last_frame_data = None


    def load_video(self):
        while True:
            img_resp = requests.get(url=self.photo_url)
            im_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
            img = cv2.imdecode(im_arr, -1)
            # newX, newY = img.shape[1], img.shape[0]
            # img = cv2.resize(img, (int(newX), int(newY)))
            # cv2.imshow("AndroidCam", img)
            self.analyze(img)
            if cv2.waitKey(1) == 27:
                break

    def start_image_getting(self):
        t_imget = threading.Thread(target=self.image_get_thread,
                                   args=[self.q])
        t_imget.start()

    def image_get_thread(self, q: LifoQueue):
        while True:
            img_resp = requests.get(url=self.photo_url)
            if q.full():
                q.get()
            q.put(img_resp)

    def load_photo_once(self, path=None):
        if path is None:
            img_resp = requests.get(url=self.photo_url)
            # img_resp = self.q.get()
            im_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
            img = cv2.imdecode(im_arr, -1)
        else:
            img = cv2.imread(path)
        return self.analyze(img)

    def load_photo(self, path=None):
        if path is None:
            # img_resp = requests.get(url=self.photo_url)
            img_resp = self.q.get()
            im_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
            img = cv2.imdecode(im_arr, -1)
        else:
            img = cv2.imread(path)

        return self.analyze(img)

    def analyze(self, frame):
        # sd = ShapeDetector()

        try:
            frame_data = self.shape_detector.analyze_image(frame, self.config["camera_settings"]["resize"])
            # print("board: " + str(frame_data[0]) + "\nmarker: " + str(frame_data[1]) + "\ntriangle: " + str(frame_data[2]))
            self.last_frame_data = frame_data
            return frame_data
        except ValueError as e:
            print("IMAGE ERROR")
            print(e)
            return self.last_frame_data

