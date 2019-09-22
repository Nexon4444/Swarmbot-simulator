config = {
  "simulation_settings":{
    "simple_commands": False,
    "wait_time": 1
  },
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
    "photo_url": "http://192.168.60.57:8080/shot.jpg",
    "launch_analysis_windows": False,
    "resize": 0.5,
    "shape_tolerance": 0.04,
    "gray_scale_threshold": 90,
    "remember_first": True
  },
  "board_settings": {
    "real_width": 100,
    "real_height": 150
  },
  "real_settings": {
    "pwm": 0.4,
    "cm_per_sec": 56.93,
    "deg_per_sec": 450,
    "gauss": {
      "x": (56, 5.32),
      "y": (0.8, 5.32)
    }
  },
  "bot_settings": {
    "view_mode_is_omni": True,
    "separation_distance": 50,
    "alignment_distance": 200,
    "cohesion_distance": 200,
    "exclusion_distance": 10,

    "sep_mul": 10.5,
    "ali_mul": 1.0,
    "coh_mul": 1.0,

    "max_speed": 5,
    "max_force": 1,

    "width": 20,
    "height": 40,
  },
  "bots": [
    {
      "bot_id": "1",
      "poz_x": 100,
      "poz_y": 100,
      "is_real": True,
      "speed": [
        5,
        1
      ],
      "color": "RED",
      "direction": 180
    }
  ]
}