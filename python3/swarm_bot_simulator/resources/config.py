config = {

  "view_settings":{
    "launch": True
  },
  "communication_settings": {
    "method_is_direct": True,
    "server_path": "E:\\mosquitto\\mosquitto.exe",
    "broker": "localhost",
    "port": 2000

  },
  "camera_settings": {
    "photo_url": "http://192.168.0.108:8080/shot.jpg",
    "launch_analysis_windows": False,
    "resize": 0.5
  },
  "bot_settings": {
    "view_mode_is_omni": True,
    "separation_distance": 100,
    "alignment_distance": 200,
    "cohesion_distance": 200,
    "exclusion_distance": 10,

    "sep_mul": 4.5,
    "ali_mul": 2.0,
    "coh_mul": 1.0,

    "max_speed": 5,
    "max_force": 1,

    "width": 20,
    "height": 40,

    "left_motor": (-9, -15),
    "right_motor": (-9, 15),
    "center_mass": (0, 0),
    "mass": 200,
    "inertia": "SQUARE"






  },
  "bots": [
    {
      "bot_id": "1",
      "poz_x": 100,
      "poz_y": 100,
      "is_real": False,
      "speed": [
        5,
        1
      ],
      "color": "RED",
      "direction": 180
    },
    {
      "bot_id": "2",
      "poz_x": 150,
      "poz_y": 200,
      "is_real": False,
      "speed": [
        4,
        1
      ],
      "color": "BLUE",
      "direction": 180
    }
  ]
}