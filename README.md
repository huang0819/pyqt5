# Data collect

Collect data.

## Description

Collect data.

## Getting Started

### Dependencies

* Python 3.9.2
* numpy==1.19.5
* PyQt5==5.15.2
* requests==2.25.1
* RPi.GPIO==0.7.0

### Installing

* main.sh
```=shell script
#!/bin/bash

cd /home/pi/pyqt5
git pull
python main.py
```

* test.sh
```=shell script
#!/bin/bash

cd /home/pi/pyqt5
git pull
python test.py
```

* After creating above files `sudo chmod +x main.sh` and  `sudo chmod +x test.sh`

### Executing program

* run main
```
python main.py
```

* run main with and show log in terminal
```
python main.py -sl
```

* test module
```
python test.py
```

* test module and show log in terminal
```
python test.py -sl
```

## Help

Any advise for common problems or issues.
```
python main.py -h
```

## Authors

## Version History

## License

## Acknowledgments
