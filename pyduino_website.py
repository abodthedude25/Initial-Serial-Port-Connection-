
from flask import Flask, render_template, request, redirect, url_for, session
from pyduino import Arduino
import serial.tools.list_ports as port_list
import time

app = Flask(__name__)
app.secret_key = "pizzahut"

# declare the pins we're using
LED_PIN = 13
ANALOG_PIN = 2
a = ''

# we are able to make 2 different requests on our webpage
# GET = we just type in the url
# POST = some sort of form submission like a button
@app.route('/', methods = ['POST','GET'])
def home_page():
    global a
    session['initialized'] = False

    ##finding all the usb ports that are in use
    ports = list(port_list.comports())
    devicesConnected = []

    for plugin in ports:
        devicesConnected.append(plugin.device)

    devicesConnected = list(devicesConnected)

    # if we make a post request on the webpage aka press button then do stuff
    if request.method == 'POST' and request.form['radio'] and not session['initialized']:
        # initialize connection to Arduino
        # if your arduino was running on a serial port other than 'COM4'
        # declare: a = Arduino(serial_port='THAT_SERIAL_PORT')
        a = Arduino(request.form['radio'])
        time.sleep(1)

        session['initialized'] = True

        # initialize the digital pin as output
        a.set_pin_mode(LED_PIN,'O')

        ##Flashing LED to indicate starting
        for i in range(0,10):
            a.digital_write(LED_PIN,((i+1)%2))
            time.sleep(0.4)
            
        return redirect( url_for('control_sensor') )

    return render_template('home.html', devicesConnected=devicesConnected)


@app.route('/controls', methods = ['POST','GET'])
def control_sensor():
    global a

    if session['initialized']:
        # if we make a post request on the webpage aka press button then do stuff
        if request.method == 'POST':

            # if we press the turn on button
            if request.form['submit'] == 'Turn On': 
                print ('TURN ON')
        
                # turn on LED on arduino
                a.digital_write(LED_PIN,1)
                

            # if we press the turn off button
            elif request.form['submit'] == 'Turn Off': 
                print ('TURN OFF')

                # turn off LED on arduino
                a.digital_write(LED_PIN,0)

        # read in analog value from photoresistor, acts with all the buttons
        readval = a.analog_read(ANALOG_PIN)
            
        # the default page to display will be our template with our template variables
        return render_template('controls.html', value=100*(readval/1023.))
    else:
        return redirect( url_for('home_page') )


# unsecure API urls
@app.route('/controls/turnon', methods=['GET'] )
def turn_on():
    global a

    # turn on LED on arduino
    if session['initialized']:
        a.digital_write(LED_PIN,1)

    return redirect( url_for('control_sensor') )


@app.route('/controls/turnoff', methods=['GET'] )
def turn_off():
    global a

    # turn off LED on arduino
    if session['initialized']:
        a.digital_write(LED_PIN,0)
    return redirect( url_for('control_sensor') )

@app.route('/controls/refreshsensor', methods=['GET'] )
def refresh():
    ##sends back to homepage, which automatically re-reads senor value
    return redirect( url_for('control_sensor') )


if __name__ == "__main__":
    app.run(debug=True)
