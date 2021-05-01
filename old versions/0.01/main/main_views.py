@main.route('/home')
@login_required
def home():
    building_info = Customer.query.get(current_user.customer_id)
    current_weather = EdmontonWeather.query.order_by(EdmontonWeather.id.desc()).first()
    r = requests.get('https://api.openweathermap.org/data/2.5/weather?q=edmonton&appid=b543e04dda3e7a9ada2c9f3cd28e6db6')
    r = r.json()
    current_temp= float((r["main"]["temp"])-273.15)
    current_condition = r['weather'][0]['main']
    temperature = int((r["main"]["temp"])-273.15)
    icon = r['weather'][0]['icon']
    heating_usage = 0
    current_regress = 0
    building_info = Customer.query.get(current_user.customer_id)
    x = TMY_Edmonton.query.all()
    furnace_output = (building_info.building_feet)*50
    current_regress = 0
    light_usage = building_info.building_feet* (0.5/1000)*0.0036
    appliance_usage = building_info.building_feet*(1.0/1000)*0.0036
    dhw_usage = 10.0
    ventilation_usage = 10*0.0036
    for row in x:
        current_regress = 1 - (row.dry_bulb_temperature + 45)/(22.5 +45)
        heating_usage = heating_usage+(furnace_output*current_regress*(1/0.8))
    heating_cost = round(heating_usage*4.5/947817.0777491506,2)
    dhw_cost = round(dhw_usage *4.5,2)
    light_cost = round((light_usage*0.11)/0.0036,2)
    appliance_cost = round((appliance_usage*0.11)/0.0036,2)
    ventilation_cost = round((ventilation_usage*0.11)/0.0036,2)
    lighting_appliance_cost = 1200
    lighting_appliance_usage = round((light_usage+appliance_usage),2)
    cost_without_solar = heating_cost+dhw_cost+lighting_appliance_cost+ventilation_cost
    cost_with_solar = heating_cost+dhw_cost
    eui = round(((dhw_usage+ventilation_usage+appliance_usage+light_usage+(furnace_output/947817.0777491506))*8760)/building_info.building_feet,2)


    return render_template('home.html', title='home',customer=building_info,light_usage=light_usage,dhw_usage=dhw_usage,lighting_appliance_usage = lighting_appliance_usage,furnace_output = furnace_output, heating_cost = heating_cost, dhw_cost = dhw_cost,
        light_cost = light_cost, appliance_cost = appliance_cost, ventilation_cost = ventilation_cost,
        lighting_appliance_cost= lighting_appliance_cost,current_temp=current_temp, temperature=temperature,
        current_condition=current_condition,icon=icon,cost_without_solar=cost_without_solar, cost_with_solar=cost_with_solar,eui=eui,
            last_updated=dir_last_updated())



@main.route('/window', methods=['GET', 'POST'])
def add_window():
    customer = Customer.query.get(current_user.customer_id)
    windows = Window.query.filter_by(customer_id=customer.id).all()
    if windows == None :
        form = WindowsForm(request.form)
        if request.method == 'POST':
            if form.validate_on_submit():
                customer = Customer.query.get(current_user.customer_id)
                for window in form.windows.data:
                    window.update({'customer_id': customer.id})
                    new_window = Window(**window)
                    db.session.add(new_window)
                    db.session.commit()
    else:
        form = WindowForm(
            length = "",
            height = "",
            location = "",
            room_type =""
        )
    return render_template("window.html", title="Add Window", form=form, last_updated=dir_last_updated())

@main.route('/audit', methods=['GET', 'POST'])
@login_required
def audit():
    if request.method == "POST":
        heatingType = request.form ["heatingType"]
        heatingAge = request.form["heatingAge"]
        heatingCapacity = request.form["heatingCapacity"]
        waterHeatingType = request.form["waterHeatingType"]
        waterHeatingAge = request.form["waterHeatingAge"]
        storageVolume = request.form ["storageVolume"]
        inputCapacity = request.form["inputCapacity"]
        fridgeCount = request.form["fridgeCount"]
        freezerCount = request.form["freezerCount"]
        microwaveCount = request.form["microwaveCount"]
        blenderCount = request.form["blenderCount"]
        coffeeMakerCount = request.form["coffeeMakerCount"]
        computerCount = request.form["computerCount"]
        dishwasherCount = request.form["dishwasherCount"]
        washerCount = request.form["washerCount"]
        dryerCount = request.form["dryerCount"]
        garageOpenerCount = request.form["garageOpenerCount"]
        kettleCount = request.form["kettleCount"]
        ovenCount = request.form["ovenCount"]
        toasterCount = request.form["toasterCount"]
        toasterOvenCount = request.form["toasterOvenCount"]
        sumpPumpCount = request.form["sumpPumpCount"]
        vacuumCount = request.form["vacuumCount"]
        customer = Customer.query.get(current_user.customer_id)
        equipment = customer.equipment
        if equipment == None:
            new_audit = Equipment(heatingType = heatingType,
            heatingAge = heatingAge,
            heatingCapacity = heatingCapacity,
            waterHeatingAge = waterHeatingAge,
            waterHeatingType = waterHeatingType,
            inputCapacity = inputCapacity, fridgeCount=fridgeCount, freezerCount=freezerCount, microwaveCount=microwaveCount, blenderCount=blenderCount, coffeeMakerCount=coffeeMakerCount,
                              computerCount=computerCount, dishwasherCount=dishwasherCount, washerCount=washerCount, dryerCount=dryerCount,
                              garageOpenerCount=garageOpenerCount, kettleCount=kettleCount, ovenCount=ovenCount, toasterCount=toasterCount,
                              toasterOvenCount=toasterOvenCount, sumpPumpCount=sumpPumpCount, vacuumCount=vacuumCount, customer_id=customer.id)
            db.session.add(new_audit)
        else:
            equipment.heatingCapacity = heatingCapacity
            equipment.heatingType = heatingType
            equipment.heatingAge = heatingAge
            equipment.waterHeatingAge = waterHeatingAge
            equipment.waterHeatingType = waterHeatingType
            equipment.inputCapacity = inputCapacity
            equipment.fridgeCount = fridgeCount
            equipment.freezerCount = freezerCount
            equipment.microwaveCount=microwaveCount
            equipment.blenderCount=blenderCount
            equipment.coffeeMakerCount=coffeeMakerCount
            equipment.computerCount=computerCount
            equipment.dishwasherCount=dishwasherCount
            equipment.washerCount=washerCount
            equipment.dryerCount=dryerCount
            equipment.garageOpenerCount = garageOpenerCount
            equipment.kettleCount = kettleCount
            equipment.ovenCount = ovenCount
            equipment.toasterCount = toasterCount
            equipment.toasterOvenCount = toasterOvenCount
            equipment.sumpPumpCount = sumpPumpCount
            equipment.vacuumCount = vacuumCount
        db.session.commit()
        return redirect(url_for('main.overview'))
    else:
        return render_template('diyAudit.html',title='Do-Yourself-Audit', last_updated=dir_last_updated())


@main.route('/street_map',methods=['GET', 'POST'])
@login_required
def get_longitude_and_latitude():
    customer = Customer.query.get(current_user.customer_id)
    return render_template('street_map_customer.html',title='Street Map',customer=customer, last_updated=dir_last_updated())


@main.route('/hotwater',methods=['GET', 'POST'])
@login_required
def hotwater():
    building_info = Customer.query.get(current_user.customer_id)
    current_weather = EdmontonWeather.query.order_by(EdmontonWeather.id.desc()).first()
    #current_temp = current_weather.temperature
    furnace_output = (building_info.building_feet)*50*(2.5/4)
    output = 30
    rvalue = 12
    heighttank = 5
    rvalue = 12
    heightank = 5
    gravity = 32.174*3600*3600
    mixed_water_temp  = 40.6
    mixed_water_temp_fahrenheit = (mixed_water_temp*(9/5))+32
    ambient_temperature = 22.5
    ambient_temperature_fahrenheit = (ambient_temperature*(9/5))+32
    tankvolume = 35
    air_density = (9.7794*(10**(-16))*(ambient_temperature**6)-0.00000000000104438738*(ambient_temperature**5) + 0.00000000040582770153*(ambient_temperature**4)-0.00000007793160224894*(ambient_temperature**3)+0.0000139445206721191*(ambient_temperature**2)-0.00425395065332666*ambient_temperature+1.28252222279131)*0.0623
    air_dynamic_viscosity = ((4.2335*(10**-16)*ambient_temperature**6-0.00000000000019274775*ambient_temperature**5-0.00000000007340906814*ambient_temperature**4+0.00000006985378704768*ambient_temperature**3-0.0000415678183959202*ambient_temperature**2+0.0495879959302156*ambient_temperature+17.2300706085878)*10**(-6))*2411.9686
    air_thermal_conductivity  =(6.63*(10**(-18))*ambient_temperature**6 - (4.65037*(10**-15))*ambient_temperature**5 + 0.00000000000037999011*ambient_temperature **4 + 0.00000000026304081567*ambient_temperature**3 - 0.00000005374945618218*ambient_temperature**2 + 0.0000744509174472757*ambient_temperature  + 0.024225420692397)*0.58
    air_specific_heat  = ((9.227*(10**(-17))*ambient_temperature**6-0.0000000000000788933*ambient_temperature**5+0.00000000001871938721*ambient_temperature**4-0.00000000051361083903*ambient_temperature**3+0.00000024455950031143*ambient_temperature**2+0.0000182814596129314*ambient_temperature+1.00502296478241)*1000)*0.000238846
    air_diffusion_rate = air_thermal_conductivity/(air_density*air_specific_heat)
    air_prandtl_number = (air_specific_heat*air_dynamic_viscosity)/air_thermal_conductivity
    outer_tank_diamter =  2*math.sqrt(tankvolume/(3.14159265359*heighttank*7.48052))
    outer_tank_radius = outer_tank_diamter/2
    inner_tank_radius = outer_tank_radius-(1/24)
    k_tank = (1/24)/rvalue
    flue_inside = 0.15*outer_tank_diamter
    flue_thickness = 0.08/12
    flue_outside = flue_inside + flue_thickness
    surface_temperature_sides = 75.5

    ra_sides = (gravity*(1/ambient_temperature_fahrenheit)*(surface_temperature_sides-ambient_temperature_fahrenheit)*(heighttank**3))/(air_diffusion_rate*air_dynamic_viscosity)
    nu_sides = (0.825+((0.387 * ra_sides**(1/6) / ((1+((0.492/air_prandtl_number)**(9/16)))**(8/27)))))**2
    h_sides =(air_thermal_conductivity*nu_sides)/(heighttank)
    surface_temperature_top = 75.5

    ra_top =(gravity*(1/ambient_temperature_fahrenheit)*(surface_temperature_top-ambient_temperature_fahrenheit)*((0.25*3.14159265359*(outer_tank_diamter**2))/((3.14159265359*outer_tank_diamter)))**3)/(air_diffusion_rate*air_dynamic_viscosity)
    nu_top = 0.54*(ra_top**(1/4))
    h_top = (air_thermal_conductivity*nu_top)/((0.25*3.14159265359*(outer_tank_diamter**2))/(3.14159265359*outer_tank_diamter))
    return render_template('hotwater.html',title='Hot Water',output = output, rvalue=rvalue,
        heighttank = heighttank, gravity=gravity,mixed_water_temp=mixed_water_temp,mixed_water_temp_fahrenheit=mixed_water_temp_fahrenheit,
        ambient_temperature_fahrenheit = ambient_temperature_fahrenheit,tankvolume=tankvolume,
        air_density=air_density,air_dynamic_viscosity=air_dynamic_viscosity,
        air_thermal_conductivity=air_thermal_conductivity,air_specific_heat=air_specific_heat,air_diffusion_rate=air_diffusion_rate,
        air_prandtl_number=air_prandtl_number,outer_tank_diamter = outer_tank_diamter,
        outer_tank_radius=outer_tank_radius,inner_tank_radius=inner_tank_radius,
        k_tank=k_tank, flue_inside=flue_inside,flue_thickness=flue_thickness, flue_outside=flue_outside,surface_temperature_sides = surface_temperature_sides,
        ra_sides=ra_sides,nu_sides=nu_sides,h_sides=h_sides,surface_temperature_top=surface_temperature_top,
        ra_top = ra_top, nu_top=nu_top, h_top=h_top, heightank = heightank, last_updated=dir_last_updated())






@main.route('/heating')
@login_required
def heating():
    building_info = Customer.query.get(current_user.customer_id)
    r = requests.get('https://api.openweathermap.org/data/2.5/weather?q=edmonton&appid=b543e04dda3e7a9ada2c9f3cd28e6db6')
    r = r.json()
    current_temp= float((r["main"]["temp"])-273.15)
    current_condition = r['weather'][0]['main']
    temperature = int((r["main"]["temp"])-273.15)
    icon = r['weather'][0]['icon']

# Roof Area calculation
    roof_area = (building_info.first_story_sf*(math.tan(22*(math.pi/180))))+(building_info.first_story_sf/(math.cos(22*(math.pi/180))))
        # Creating Wall Square Footage Distrubution based upon home type
    if building_info.building_description == "1 1/2 Storey & Basement":
        wall_area = ((math.sqrt(building_info.first_story_sf/21)*20)*8)+((math.sqrt(building_info.first_story_sf/21)*20)*4)
        basement_wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
    elif building_info.building_description == "1 1/2 Sty. Slab on Grade":
        wall_area = ((math.sqrt(building_info.first_story_sf/21)*20)*8)+((math.sqrt(building_info.first_story_sf/21)*20)*4)
        basement_wall_area = 0
    elif building_info.building_description == "1 3/4 Storey & Basement":
        wall_area = ((math.sqrt(building_info.first_story_sf/21)*20)*(16/3))+((math.sqrt(building_info.first_story_sf/21)*20)*2)
        basement_wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
    elif building_info.building_description == "1 3/4 Storey Basementless":
        wall_area = ((math.sqrt(building_info.first_story_sf/21)*20)*(16/3))+((math.sqrt(building_info.first_story_sf/21)*20)*2)
        basement_wall_area = 0
    elif building_info.building_description == "1 3/4 Sty. Slab on Grade":
        wall_area = ((math.sqrt(building_info.first_story_sf/21)*20)*(16/3))+((math.sqrt(building_info.first_story_sf/21)*20)*2)
        basement_wall_area = 0
    elif building_info.building_description == "1 Storey & Basement":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
        basement_wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
    elif building_info.building_description == "1 Storey & Bonus Upper":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
        basement_wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
    elif building_info.building_description == "1 Storey Basementless":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
        basement_wall_area = 0
    elif building_info.building_description == "1 Storey Slab on Grade":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
        basement_wall_area = 0
    elif building_info.building_description == "1 Storey Upper":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
        basement_wall_area = 0
    elif building_info.building_description == "2 Storey & Basement":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*16
        basement_wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
    elif building_info.building_description == "2 Storey Basementless":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*16
        basement_wall_area = 0
    elif building_info.building_description == "2 Storey Slab on Grade":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*16
        basement_wall_area = 0
    elif building_info.building_description == "3 Storey & Basement":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*24
        basement_wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
    elif building_info.building_description == "3 Storey Basementless":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*24
        basement_wall_area = 0
    elif building_info.building_description == "Split Entry":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*10
        basement_wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
    elif building_info.building_description == "Split Entry & Bonus Upper":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*10
        basement_wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
    elif building_info.building_description == "Split Level":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*10
        basement_wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*8
    elif building_info.building_description == "Split Level & Crawl Space":
        wall_area = (math.sqrt(building_info.first_story_sf/21)*20)*10
        basement_wall_area = 0
    if building_info.year_built <= 1920:
        wall_rvalue  = 0
        roof_rvalue  = 2
    elif building_info.year_built > 1920 and building_info.year_built <= 1949:
        wall_rvalue = 6
        roof_rvalue = 8
    elif building_info.year_built > 1949 and building_info.year_built <= 1969:
        wall_rvalue = 8
        roof_rvalue = 12
    elif building_info.year_built > 1969 and building_info.year_built <= 1979:
        wall_rvalue = 12
        roof_rvalue = 30
    elif building_info.year_built > 1979 and building_info.year_built <= 2111:
        wall_rvalue = 20
        roof_rvalue = 40
    furnace_output = (building_info.building_feet)*50*(3/4)
    current_regress = 1 - (current_temp + 45)/(22.5 +45)
    hour_output = furnace_output*current_regress*(1/0.8)
    yearly_heating_usage = 0
    regress_TMY = 0
    x = TMY_Edmonton.query.all()
    length = math.sqrt(building_info.building_feet/21)*7
    width = math.sqrt(building_info.building_feet/21)*3
    furnace_output = (building_info.building_feet)*50*(3/4)
    individual_windows_UA_cost = {
    "window1_livingroom": 0.0111,
    "widnow2_bathroom": 0.0222
        }
    UA_walls = wall_area*(1/wall_rvalue)*5
    UA_windows = 0
    UA_doors = (1/3.5)*48*5
    UA_basement = basement_wall_area*(1/8)*5
    UA_roof = roof_area*(1/roof_rvalue)*5
    for row in x:
        regress_TMY = 1 - (row.dry_bulb_temperature + 45)/(22.5 +45)
        yearly_heating_usage = yearly_heating_usage+(furnace_output*regress_TMY*(1/0.8))
    wall_loss_total = 5.0*4.5
    window_loss_total = 1.0*4.5
    door_loss_total = 1.2*4.5
    basement_loss_total = 2.5*4.5
    roof_loss_total = 7.0*4.5
    individual_windows_annual_cost = {
    "window1_livingroom": 1.2,
    "widnow2_bathroom": 1.5
        }
    r = requests.get('https://api.openweathermap.org/data/2.5/weather?q=edmonton&appid=b543e04dda3e7a9ada2c9f3cd28e6db6')
    r = r.json()
    current_temp= float((r["main"]["temp"])-273.15)
    current_condition = r['weather'][0]['main']
    temperature = int((r["main"]["temp"])-273.15)
    icon = r['weather'][0]['icon']



    return render_template('heating.html', title='he
        @main.route('/lighting/',methods=['GET', 'POST'])
@login_required
def lighting():
    customer = Customer.query.get(current_user.customer_id)
    return render_template('lighting.html',title='Lighting',customer=customer, last_updated=dir_last_updated())


@main.route('/heatinginfo', methods=['GET', 'POST'])
@login_required
def furnace():
    if request.method == "POST":
        heatingType = request.form ["heatingType"]
        heatingAge = request.form["heatingAge"]
        heatingCapacity = request.form["heatingCapacity"]
        customer = Customer.query.get(current_user.customer_id)
        equipment = customer.equipment
        if equipment == None:
            new_audit = Equipment(heatingType = heatingType,
            heatingAge = heatingAge,
            heatingCapacity = heatingCapacity,
            customer_id=customer.id)
            db.session.add(new_audit)
        else:
            equipment.heatingCapacity = heatingCapacity
            equipment.heatingType = heatingType
            equipment.heatingAge = heatingAge
        db.session.commit()
        return redirect(url_for('main.heating'))
    else:
        return render_template('furnaceInfo.html',title='Add Furnace', last_updated=dir_last_updated())




@main.route('/hotwaterinfo', methods=['GET', 'POST'])
@login_required
def hotwatertank():
    if request.method == "POST":

        waterHeatingType = request.form["waterHeatingType"]
        waterHeatingAge = request.form["waterHeatingAge"]
        storageVolume = request.form ["storageVolume"]
        inputCapacity = request.form["inputCapacity"]

        customer = Customer.query.get(current_user.customer_id)
        equipment = customer.equipment
        if equipment == None:
            new_audit = Equipment(
            waterHeatingAge = waterHeatingAge,
            waterHeatingType = waterHeatingType,
            inputCapacity = inputCapacity,customer_id=customer.id)
            db.session.add(new_audit)
        else:
            equipment.waterHeatingAge = waterHeatingAge
            equipment.waterHeatingType = waterHeatingType
            equipment.inputCapacity = inputCapacity
        db.session.commit()
        return redirect(url_for('main.hotwater'))
    else:
        return render_template('hotwaterInfo.html',title='Add Hot Water Tank', last_updated=dir_last_updated())
ating',icon = icon, UA_walls = UA_walls, UA_windows= UA_windows,
     UA_doors = UA_doors, UA_roof = UA_roof, wall_loss_total = wall_loss_total, window_loss_total = window_loss_total,
     door_loss_total = door_loss_total, basement_loss_total = basement_loss_total, roof_loss_total=roof_loss_total,

        temperature = temperature, current_condition = current_condition, current_temp=current_temp,furnace_output=furnace_output,
        last_updated=dir_last_updated())





@main.route('/pace/',methods=['GET', 'POST'])
@login_required
def pace():
    return render_template('pace.html',title='PACE', last_updated=dir_last_updated())

@main.route('/kpi',methods=['GET', 'POST'])
@login_required
def kpi():
    return render_template('kpi.html',title='Overview', last_updated=dir_last_updated())



@main.route('/solar/',methods=['GET', 'POST'])
@login_required
def solar():
    customer = Customer.query.get(current_user.customer_id)
    return render_template('solar.html',title='Solar',customer=customer, last_updated=dir_last_updated())


@main.route('/lighting/',methods=['GET', 'POST'])
@login_required
def lighting():
    customer = Customer.query.get(current_user.customer_id)
    return render_template('lighting.html',title='Lighting',customer=customer, last_updated=dir_last_updated())


@main.route('/heatinginfo', methods=['GET', 'POST'])
@login_required
def furnace():
    if request.method == "POST":
        heatingType = request.form ["heatingType"]
        heatingAge = request.form["heatingAge"]
        heatingCapacity = request.form["heatingCapacity"]
        customer = Customer.query.get(current_user.customer_id)
        equipment = customer.equipment
        if equipment == None:
            new_audit = Equipment(heatingType = heatingType,
            heatingAge = heatingAge,
            heatingCapacity = heatingCapacity,
            customer_id=customer.id)
            db.session.add(new_audit)
        else:
            equipment.heatingCapacity = heatingCapacity
            equipment.heatingType = heatingType
            equipment.heatingAge = heatingAge
        db.session.commit()
        return redirect(url_for('main.heating'))
    else:
        return render_template('furnaceInfo.html',title='Add Furnace', last_updated=dir_last_updated())




@main.route('/hotwaterinfo', methods=['GET', 'POST'])
@login_required
def hotwatertank():
    if request.method == "POST":

        waterHeatingType = request.form["waterHeatingType"]
        waterHeatingAge = request.form["waterHeatingAge"]
        storageVolume = request.form ["storageVolume"]
        inputCapacity = request.form["inputCapacity"]

        customer = Customer.query.get(current_user.customer_id)
        equipment = customer.equipment
        if equipment == None:
            new_audit = Equipment(
            waterHeatingAge = waterHeatingAge,
            waterHeatingType = waterHeatingType,
            inputCapacity = inputCapacity,customer_id=customer.id)
            db.session.add(new_audit)
        else:
            equipment.waterHeatingAge = waterHeatingAge
            equipment.waterHeatingType = waterHeatingType
            equipment.inputCapacity = inputCapacity
        db.session.commit()
        return redirect(url_for('main.hotwater'))
    else:
        return render_template('hotwaterInfo.html',title='Add Hot Water Tank', last_updated=dir_last_updated())
