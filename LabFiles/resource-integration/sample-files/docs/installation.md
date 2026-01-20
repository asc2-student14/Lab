# Installation Guide

## Hardware Setup

### Required Components
- BeanBotics RB-3000 Robotic Arm
- Precision Grinder Module (PGM-400)
- Dual Boiler System (DBS-Pro)
- Customer Interface Display (CID-Touch)

### Assembly Steps

1. **Mount the robotic arm** to the base platform using the provided bolts
2. **Connect the grinder module** to the arm's tool mount
3. **Install the dual boiler system** in the designated compartment
4. **Attach water lines** from reservoir to boiler inlet
5. **Connect all electrical components** following the wiring diagram

## Software Installation

```bash
# Clone the BeanBotics software
git clone https://github.com/beanbotics/rb3000-firmware.git

# Install dependencies
pip install -r requirements.txt

# Run initial setup
python setup.py install
```

## Calibration

Run the calibration wizard to ensure optimal performance:

```bash
python calibrate.py --full-calibration
```

This process takes approximately 15 minutes and includes:
- Arm movement range verification
- Grinder blade alignment
- Temperature sensor calibration
- Scale precision testing