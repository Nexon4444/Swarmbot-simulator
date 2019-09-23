config = {
  "simulation_settings":{
    "simple_commands": False,
    "wait_time": 1.0
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
    "real_width": 94,
    "real_height": 83.5
  },
  "real_settings": {
    "pwm": 0.3,
    "pwm_forward": 0.7,
    # "cm_per_sec": 56.93,
    "cm_per_sec": 25.69,
    "deg_per_sec": 145,
    "gauss": {
      "x": (0.8, 5.32),
      "y": (56, 5.32)
    }
  },
  "bot_settings": {
    "view_mode_is_omni": True,
    "separation_distance": 100,
    "alignment_distance": 300,
    "cohesion_distance": 300,
    "exclusion_distance": 10,

    "sep_mul": 10.5,
    "ali_mul": 0.5,
    "coh_mul": 0.5,

    "max_speed": 5,
    "max_force": 5,

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
    },
    {
      "bot_id": "2",
      "poz_x": 150,
      "poz_y": 100,
      "is_real": False,
      "speed": [
        4,
        1
      ],
      "color": "BLUE",
      "direction": 180
    },
    {
      "bot_id": "3",
      "poz_x": 100,
      "poz_y": 150,
      "is_real": False,
      "speed": [
        4,
        1
      ],
      "color": "BLUE",
      "direction": 180
    },
    {
      "bot_id": "4",
      "poz_x": 150,
      "poz_y": 150,
      "is_real": False,
      "speed": [
        4,
        1
      ],
      "color": "BLUE",
      "direction": 180
    },
    {
          "bot_id": "5",
          "poz_x": 170,
          "poz_y": 150,
          "is_real": False,
          "speed": [
              5,
              1
          ],
          "color": "BLUE",
          "direction": 180
      },
      {
          "bot_id": "6",
          "poz_x": 150,
          "poz_y": 170,
          "is_real": False,
          "speed": [
              4,
              1
          ],
          "color": "BLUE",
          "direction": 180
      },
      {
          "bot_id": "7",
          "poz_x": 200,
          "poz_y": 150,
          "is_real": False,
          "speed": [
              4,
              1
          ],
          "color": "BLUE",
          "direction": 180
      },
      {
          "bot_id": "8",
          "poz_x": 150,
          "poz_y": 200,
          "is_real": False,
          "speed": [
              4,
              11
          ],
          "color": "BLUE",
          "direction": 180
      },

  ]
}