def bet_49ja_script(name, version, remote_url, user_id):
    bet9ja = r"""import json, sys, os, csv, time, pyautogui
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys 
from stdiomask import getpass
import requests
chrome_options = Options()

chrome_options.add_argument("--headless")
basedir = os.path.abspath(os.path.dirname(__file__))

browser = webdriver.Chrome("./chromedriver.exe")
pyautogui.hotkey('alt', '\t')
try:
    with open('C:\ProgramData\SRB\conf.json', 'r') as config:
        config = json.load(config)
        bot_type = config.get("bot_type")
        if bot_type == "demo":
            demo_start_date = config.get('demo_start_date')
            expired_time = float(demo_start_date) + (0.5 * 86400)
            expires = datetime.fromtimestamp(expired_time)
            meridian = "PM" if expires.hour > 12 else "AM"
            meridian_hour = expires.hour
            if expires.hour > 12:
                median_hour = expires.hour - 12
                
            print(f"You are running a demo version of this bot\nThis bot will expire on {expires.day}-{expires.month}-{expires.year} {meridian_hour}:{expires.minute}{meridian}")
            if time.time() > expired_time:
                print("The demo version of this bot has expired, Please ")
                time.sleep(15)
                sys.exit(1)
            else:
                print("The Demo version of 49ja bot as started")
        
        elif bot_type == "paid":
            is_paid = config.get('is_active')
            if is_paid:
                pass
            else:
                print(f"You have not bought this bot, Go to {url} to purchase the bot")
                time.sleep(15)
                sys.exit(1)
                # base_url = config.get('remote_url')
                # token = input("Enter Purchase pin\n")
                # url = f"{base_url}/confirm-paid/{token}"
                # requests.get(url)
        
        elif bot_type == "subscribe":
            try:
                base_url = config.get('remote_url')
                user_id = config.get('user_id')
                url = f"{base_url}/has_subscribed?q={user_id}"
                has_sub = requests.get(url)
                has_sub.raise_for_status()
                print(has_sub.json())
                if has_sub.json().get("result"):
                    pass
                else:
                    print(f"You do not have an active connection currently, Go to {base_url} to subscribe")
                    time.sleep(15)
                    sys.exit(1)
            except Exception as exc:
                print(f"Make sure your internet connection is active or {exc}")
                time.sleep(15)
                sys.exit(1)
        else:
            pass
except Exception as exc:
    print("starting configuration settings")

class Bot:
    def __init__(self):
        self.init_bot()
        # timeout in mins
        self.url_timeout = 30 * 60
        # Second Algorithm Global Objects
        self.second_algo = 0
        self.second_algo_prediction = []
        choice = self.ask_for_input('Welcome to 49ja bot by dataslid and paulizi\n1. to start the bot\n2. for settings\n3. exit\n', 3)
        if choice == 1:
            self.start_bot()
        elif choice == 2:
            self.settings()
        elif choice == 3:
            os.system('exit()')
            time.sleep(3)
            pyautogui.hotkey('alt', 'f4')
            sys.exit(0)

    def start_bot(self):
        import time
        with open('C:\ProgramData\SRB\conf.json', 'r') as config:
            config = json.load(config)
        
        cur_time = time.time()
        is_url_active = config["checkpoint"]
        is_checkpoint_active = config["timeout"]
        
        if is_url_active and is_checkpoint_active and is_checkpoint_active > cur_time:
            color_url = config["checkpoint"]
            browser.get(color_url)
            browser.implicitly_wait(10)
            cash = browser.find_element_by_xpath("//div[@class='rs-menu__balance-value']")
            acc_bal = cash.find_element_by_tag_name('span').text
            
            config['acc_bal'] = acc_bal
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                conf.write(write_json)

            is_empty = True
            while is_empty:
                if acc_bal != "":
                    acc_bal = int(float(acc_bal))
                    type_of_bot_algo = config['bot_algorithm']
                    stop_loss = acc_bal - int(config['loss_limit'])
                    stop_profit = acc_bal + int(config['profit_limit'])
                    print(f'stop loss at {stop_loss}')
                    print(f'stop profit at {stop_profit}')
                
                    self.bot_loop(acc_bal, stop_loss, stop_profit, type_of_bot_algo)
                    is_empty = False
                else:
                    time.sleep(5)
                    cash = browser.find_element_by_xpath("//div[@class='rs-menu__balance-value']")
                    acc_bal = cash.find_element_by_tag_name('span').text
         
        else:
            url = 'https://casino.bet9ja.com/casino/category/popular'
            browser.get(url)
            browser.find_element_by_css_selector("body").send_keys(Keys.ALT, Keys.TAB)

            browser.implicitly_wait(10)
            is_login = browser.find_elements_by_class_name("h-ml__login-form")
            # print(is_login)
            if len(is_login) > 0:
                with open('C:\ProgramData\SRB\conf.json', 'r') as config:
                    config = json.load(config)
                username = browser.find_element_by_xpath("//input[@type='text']").send_keys(config['username'])
                password = browser.find_element_by_xpath("//input[@type='password']").send_keys(config['password'])
                submit = browser.find_element_by_xpath("//button[@class='h-ml__login-btn']").click()
                time.sleep(5)
                
            browser.implicitly_wait(5)
            
            elem = browser.find_element_by_xpath("//div[@id='11000']/div/div[3]/button")
            action = webdriver.ActionChains(browser)
            action.move_to_element(elem)
            action.perform()
            elem.click()

            browser.implicitly_wait(10)

            color_url = input('=============================================================\nPlease copy the url or site address of the pop-up browser\n=============================================================\n\n')
            browser.get(color_url)
            browser.implicitly_wait(10)
            browser.implicitly_wait(10)
            
            cash = browser.find_element_by_xpath("//div[@class='rs-menu__balance-value']")
            acc_bal = cash.find_element_by_tag_name('span').text
            config['acc_bal'] = acc_bal
            config["checkpoint"] = color_url
            config["timeout"] = self.url_timeout + time.time()
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                conf.write(write_json)

            is_empty = True
            while is_empty:
                if acc_bal != "":
                    acc_bal = int(float(acc_bal))
                    stop_loss = acc_bal - int(config['loss_limit'])
                    stop_profit = acc_bal + int(config['profit_limit'])
                    type_of_bot_algo = config['bot_algorithm']
                    print(f'stop loss at {stop_loss}')
                    print(f'stop profit at {stop_profit}')
                
                    self.bot_loop(acc_bal, stop_loss, stop_profit, type_of_bot_algo)
                    is_empty = False
                else:
                    time.sleep(5)
                    cash = browser.find_element_by_xpath("//div[@class='rs-menu__balance-value']")
                    acc_bal = cash.find_element_by_tag_name('span').text
                        
    def bot_loop(self, acc_bal, stop_loss, stop_profit, type_of_bot_algo):
        # COLLECT DATA
            # if the time is less than 15 secs wait for that 15 secs
        try:
            game_time = browser.find_element_by_xpath("//div[@class='timeline__value-txt']").text
            if int(game_time) < 15:
                time.sleep(15)    
            
            # loop and play until loss or profit limit is met
            while True:
                # click the statistics button
                browser.find_element_by_xpath("//div[@class='stats__toggle ']").click()
                tableData = browser.find_element_by_xpath("//table[@class='statistics']")
                tablerow = tableData.find_elements_by_tag_name('tr')
                tablecolors = tableData.find_elements_by_xpath("//div[@class='colours']")

                # if len_of_bot_data < 9 or not has_checkpoint:
                data_for_bot = []
                for i, eachrow in enumerate(tablerow):
                    if i > 4:
                        break
                    table_winning_color = browser.find_elements_by_class_name('rainbows')[i].find_element_by_tag_name('div').get_attribute('class')[17:]
                    red_color_value = eachrow.find_elements_by_xpath("//div[@class='colours__item red']")[i].text
                    blue_color_value = eachrow.find_elements_by_xpath("//div[@class='colours__item blue']")[i].text
                    green_color_value = eachrow.find_elements_by_xpath("//div[@class='colours__item green']")[i].text
                    data_for_bot.insert(0, [table_winning_color, red_color_value, green_color_value, blue_color_value]) 

                time.sleep(5)
                browser.find_element_by_xpath("//div[@class='stats__toggle active']").click()
                new_cash = browser.find_element_by_xpath("//div[@class='rs-menu__balance-value']")
                new_acc_bal = int(float(new_cash.find_element_by_tag_name('span').text))
                
                    
                # to select the five bet type and to bet on it
                allbettypes = browser.find_elements_by_class_name("game-nav__item")
                allbettypes[4].click()

                allcolorbet = browser.find_elements_by_class_name("g-total__btn-txt")
                # Select algorithm
                if type_of_bot_algo == 1:
                    prediction = self.bot_algorithm(data_for_bot)
                elif type_of_bot_algo == 2:
                    prediction = self.sec_bot_algorithm(data_for_bot)
                elif type_of_bot_algo == 3:
                    prediction = self.third_bot_algorithm(data_for_bot)
                    
                # checking if button is active
                game_time = browser.find_element_by_xpath("//div[@class='timeline__value-txt']").text
                print(f"The current time is {game_time}")
                if prediction and int(game_time) > 9:
                    for each_prediction in prediction:
                        print(each_prediction)
                        cap_pred = each_prediction[0].upper() + each_prediction[1:] 
                        for colorbet in allcolorbet:
                            # if color == to capitalised prediction
                            if colorbet.text == cap_pred:
                                # print('it did see blue')
                                browser.find_element_by_xpath(f"//div[@class='g-total__btn {each_prediction} ']").click()
                                # pull in the config file
                                with open('C:\ProgramData\SRB\conf.json', 'r') as config:
                                    config = json.load(config)
                                    bet_stake = config['bet']
                                    
                                browser.find_element_by_xpath("//input[@type='number']").send_keys(Keys.CONTROL + "a")
                                browser.find_element_by_xpath("//input[@type='number']").send_keys(bet_stake)
                                
                                disabled = True
                                button_elem = browser.find_element_by_xpath("//a[@class='place-bet']")
                                print(f"button {button_elem.is_enabled()}")
                                while disabled:
                                    if button_elem.is_enabled():
                                        browser.find_element_by_xpath("//a[@class='place-bet']").click()
                                        disabled = False
                                    time.sleep(1)
                                print(f'bot played {each_prediction} i hope it comes!')
                        time.sleep(1)                        
                        
                else:
                    print("Cannot place bet at this time or There is no prediction")
                # sleep for secs
                if new_acc_bal <= stop_loss:
                    loss = acc_bal - new_acc_bal 
                    print(f"Sorry... You have reached your loss limit, you lost N{loss}, try again soon, you have better strategy do contact me via whatsapp +2348142700835")
                    # Play sound on quit
                    with open('C:\ProgramData\SRB\conf.json', 'r') as config:
                        config = json.load(config)
                    if config['alert_music']:
                        file_path = config['alert_music']
                        os.system(file_path)
                    sys.exit(0)
                    browser.quit()

                elif new_acc_bal >= stop_profit:
                    profit = new_acc_bal - acc_bal
                    print(f"congratulation!!! You have reached your profit limit, you won N{profit} play more soon!")
                    # Play sound on quit
                    with open('C:\ProgramData\SRB\conf.json', 'r') as config:
                        config = json.load(config)
                    if config['alert_music']:
                        file_path = config['alert_music']
                        os.system(file_path)
                    sys.exit(0)
                    browser.quit() 

                time.sleep(40)
        except Exception:
            print("some bad happened restarting bot to continue playing")
            with open('C:\ProgramData\SRB\conf.json', 'r') as config:
                config = json.load(config)
            color_url = config["checkpoint"]
            browser.get(color_url)
            browser.implicitly_wait(10)
            
            cash = browser.find_element_by_xpath("//div[@class='rs-menu__balance-value']")
            acc_bal = cash.find_element_by_tag_name('span').text
            
            config['acc_bal'] = acc_bal
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                conf.write(write_json)

            is_empty = True
            while is_empty:
                if acc_bal != "":
                    acc_bal = int(float(acc_bal))
                    stop_loss = acc_bal - int(config['loss_limit'])
                    stop_profit = acc_bal + int(config['profit_limit'])
                    type_of_bot_algo = config['bot_algorithm']
                    print(f'stop loss at {stop_loss}')
                    print(f'stop profit at {stop_profit}')
                
                    self.bot_loop(acc_bal, stop_loss, stop_profit, type_of_bot_algo)
                    is_empty = False
                else:
                    time.sleep(5)
                    cash = browser.find_element_by_xpath("//div[@class='rs-menu__balance-value']")
                    acc_bal = cash.find_element_by_tag_name('span').text

    def sec_bot_algorithm(self, dataToUse):
        if self.second_algo == 0:
            print(f"four last history {dataToUse[:1]}")
            
            prediction = []
            prediction_list = [ 'red', 'green', 'blue' ]
            
            activate_color = None

            four_color = dataToUse[1]
            if four_color[0] == 'red':
                colour_number = four_color[1]
                if colour_number == 4:
                    activate_color = 'red'
                print(f'{colour_number} red')
                    
            elif four_color[0] == 'green':
                colour_number = four_color[2]
                if colour_number == 4:
                    activate_color = 'green'
                print(f'{colour_number} green')
                
            elif four_color[0] == 'blue':
                colour_number = four_color[3]
                if colour_number == 4:
                    activate_color = 'blue'
                print(f'{colour_number} blue')
            
            activate_pattern = 0
            if activate_color:
                for each_draw in dataToUse[2:]:
                    if each_draw[0] != activate_color:
                        activate_pattern += 1

            if activate_pattern > 2:
                print("predict")
                prediction_list.remove(activate_color)
                prediction = prediction_list
                self.second_algo = 2
                self.second_algo_prediction = prediction
                print(f"{prediction[0]} and {prediction[1]} is predicted best of luck")
                
            if not prediction: 
                print('No pattern occurred so no bet!!! Bot still waiting')
            return prediction
        else: 
            self.second_algo -= 0
            prediction = self.second_algo_prediction
            return prediction

    def third_bot_algorithm(self, dataToUse):
        last_data_index = len(dataToUse) - 1
        last_data = dataToUse[last_data_index]
        colors = ['red', 'green', 'blue']
        prediction = []
        look_for_four = False
        for i in last_data[1:]:
            if int(i) > 3:
                look_for_four = True


        if 0 in last_data and look_for_four:
            pattern = last_data[1:].index(0)
            colors.remove(colors[pattern])
            prediction = colors
            print(f"{prediction[0]} and {prediction[1]} is predicted best of luck")
			
        if not prediction: 
            print('No pattern occurred so no bet!!! Bot still waiting')
        return prediction

	
    def bot_algorithm(self, dataToUse):
        # bot algorithm
        print(f"This is the data to use {dataToUse}")
        color_occurence_winning = {
            'red': 0,
            'green': 0,
            'blue': 0
        }

        prediction = []
        
        single_pattern = 0

        find_highest = 0
        highest_win_color = None
        for i, each_winning_streaking in enumerate(dataToUse[:3]):
            if each_winning_streaking[0] != 'none':
                color_occurence_winning[each_winning_streaking[0]] += 1
                print(color_occurence_winning)

        for i, each_value in enumerate(color_occurence_winning.values()):
            if each_value >= find_highest:
                find_highest = each_value
                highest_win_color = i

        highest_win_color_name = list(color_occurence_winning.keys())[highest_win_color]
        highest_win_color_list = list(color_occurence_winning.keys())
      
        print(f"{list(color_occurence_winning.keys())[highest_win_color]} is the highest winning color")
                        
            
        single_occurence = 0
        if find_highest >= 2:
            # because the name of the color is in list
            highest_win_color_index = highest_win_color + 1
            for i, singleDataToUse in enumerate(dataToUse[3:]):
                single_pattern = int(singleDataToUse[highest_win_color_index])
                if single_pattern == 1:
                    single_occurence += 1
                
        
        if single_occurence > 1:
            highest_win_color_list.remove(highest_win_color_name)
            prediction = highest_win_color_list
            print(f"{prediction[0]} and {prediction[1]} is predicted best of luck")
			
        if not prediction: 
            print('No pattern occurred so no bet!!! Bot still waiting')
        return prediction

    def init_bot(self):
        try:
            with open('C:\ProgramData\SRB\conf.json', 'r') as config:
                config = json.load(config)    
            if not config["username"]:
                unconfirmed_username = True
                username = ""
                while unconfirmed_username:
                    print('hi, congratulation for acquiring bet9ja 49ja bots\n')
                    username_value = input('set your bet9ja username, make sure it is correct because you are allowed to set it once in the bot\n')
                    username_value_comfirmed = input('confirm your username, make sure it is correct because you are allowed to set it once once in the bot\n')
                    if username_value == username_value_comfirmed:
                        unconfirmed_username = False
                        username = username_value
                        print(f'++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your bet9ja username to {username} \n++++++++++++++++++++')
                    else:
                        print('++++++++++++++++++++\nyour username and confirm username must match\n++++++++++++++++++++')
                        time.sleep(2)

                config['username'] = username
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)


            # for your bet 9ja password

            if not config["password"]:
                unconfirmed_password = True
                password = ""
                while unconfirmed_password:
                    password_value = getpass(prompt='set your bet9ja password \n')
                    password_value_comfirmed = getpass(prompt='confirm your password\n')
                    #input('confirm your password\n')
                    # password_value = input('set your bet9ja password \n')
                    if password_value == password_value_comfirmed:
                        unconfirmed_password = False
                        password = password_value
                        print(f'++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your bet9ja password to {password} \n++++++++++++++++++++')
                    else:
                        print('++++++++++++++++++++\nyour password and confirm password must match\n++++++++++++++++++++')
                        time.sleep(2)

                config['password'] = password
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)


            if not config["bet"]:
                not_enough_bet = True
                # making sure the bet is more than 
                while not_enough_bet:
                    bet_value = input('set the amount you want the bot to bet in naira e.g 100, you can always change this in the settings \n')
                    if bet_value.isdecimal():
                        if int(bet_value) >= 50:
                            config['bet'] = bet_value
                            print(f"++++++++++++++++++++\nthe bet price has been successfully set {bet_value}\n++++++++++++++++++++")
                            not_enough_bet = False
                        else:
                            print("++++++++++++++++++++\nthe least amount a bot can bet is 50\n++++++++++++++++++++")
                            time.sleep(2)
                    else:
                        print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                        time.sleep(2)

                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                    conf.write(write_json)

                time.sleep(2)

            if not config["loss_limit"]:
                no_loss_limit = True
                # making sure the bet is more than 
                while no_loss_limit:
                    loss_limit_value = input('set your loss limit in naira e.g. 1000, if you don"t set your loss limit, if you are unfortunate, the bot might run until you have lost all your funds, you can always change this in the settings \n')
                    if loss_limit_value.isdecimal():
                        if int(loss_limit_value) >= 200:
                            config['loss_limit'] = loss_limit_value
                            print(f"++++++++++++++++++++\nthe loss limit has been successfully set {loss_limit_value}\n++++++++++++++++++++")
                            no_loss_limit = False
                        else:
                            print('++++++++++++++++++++\nloss limit too small the least should be 200\n++++++++++++++++++++')
                            time.sleep(2)
                    else:
                        print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                        time.sleep(2)

            
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                    conf.write(write_json)

                time.sleep(2)

            if not config["profit_limit"]:
                no_profit_limit = True
                # making sure the bet is more than 
                while no_profit_limit:
                    profit_limit_value = input('set your profit limit in naira e.g. 1000, if you don"t set your profit limit, you might never make any profit till the bot reach loss limit and if you did not set your loss limit as well you might lose all you funds \n')
                    if profit_limit_value.isdecimal():
                        if int(profit_limit_value) >= 200:
                            config['profit_limit'] = profit_limit_value
                            print(f"++++++++++++++++++++\nthe profit limit has been successfully set {profit_limit_value}\n++++++++++++++++++++")
                            no_profit_limit = False
                        else:
                            print('++++++++++++++++++++\nprofit limit too small the least should be 200\n++++++++++++++++++++')
                            time.sleep(2)
                    else:
                        print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                        time.sleep(2)

            
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                    conf.write(write_json)

                time.sleep(2)
            
            if not config["alert_music"]:
                file_path = input('Go to Your preferred sound, copy and paste the file path e.g C:/Users/dataslid/Music/fem.mp3, You can always change this in the settings\n')
                config['alert_music'] = file_path
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)
            
            if not config["bot_algorithm"]:
                algo_value = self.ask_for_input('Set your prefered the bot algorithm\n1. This algorithm looks for a color to win two, three times consecutive and play if the color comes once afterward \n2. This algorithm looks for a color to win with 4 colors, then it waits for oppositing colors to play lose for 3 times straight then it plays the 4th time if it is a lose it doubles the stake and play the fifth time.\nYou can always change this in the settings\n3. This algorithm looks for a color to win with 4 colors and any color to be absent i.e. to have 0 color then the bot will play on two colors except that 0 color. \n', 3)
                config['bot_algorithm'] = algo_value
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\conf.json', 'w') as config:
                    config.write(write_json)
                
                time.sleep(2)

        
        except Exception:
            # 99rRtDVzfW3zjhe paulizi
            demo_start_date = time.time()
            config = {"username": "%s", "password": "", "bet": "", "loss_limit": "", "profit_limit": "", "acc_bal": "", "checkpoint": "", "timeout": "", "bot_algorithm": "", "alert_music": "", "demo_start_date": f"{demo_start_date}", "bot_type": "%s", "remote_url": "%s", "is_active": "", "user_id": "%s"}
            write_json = json.dumps(config) 
            os.chdir('C:\ProgramData')
            if 'SRB' in os.listdir():
                with open('./SRB/conf.json', 'w') as config:
                    config.write(write_json)
            else:
                os.system("mkdir SRB")
                with open('./SRB/conf.json', 'w') as config:
                    config.write(write_json)
                    
            self.init_bot()
 
    def settings(self):
        choice = self.ask_for_input('what do you want to change?\n1. bet price\n2. bet9ja password\n3. loss limit\n4. profit limit\n5. bot algorithm\n6. change sound file name\n', 6) 

        if choice == 1:
            self.bot_settings("bet")

        elif choice == 2:
            self.bot_settings("password")

        elif choice == 3:
            self.bot_settings("loss_limit")
        
        elif choice == 4:
            self.bot_settings("profit_limit")
        
        elif choice == 5:
            self.bot_settings("bot_algorithm")

        elif choice == 6:
            self.bot_settings("alert_music")



    def bot_settings(self, arg):
        with open('C:\ProgramData\SRB\conf.json', 'r') as config:
            config = json.load(config)

        if arg == "bet":
            print(f"\nThe current bet price is set to {config['bet']}\n")
            not_enough_bet = True
            # making sure the bet is more than 
            while not_enough_bet:
                bet_value = input('reset the amount you want the bot to bet in naira e.g 100\n')
                if bet_value.isdecimal():
                    if int(bet_value) >= 50:
                        config['bet'] = bet_value
                        print(f"++++++++++++++++++++\nthe bet price has been successfully set {bet_value}\n++++++++++++++++++++")
                        not_enough_bet = False
                    else:
                        print("++++++++++++++++++++\nthe least amount a bot can bet is 50\n++++++++++++++++++++")
                        time.sleep(2)
                else:
                    print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                    time.sleep(2)

            write_json = json.dumps(config)
            with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                conf.write(write_json)

            time.sleep(2)
            self.__init__()

        elif arg == "loss_limit":
            print(f"\nThe current loss limit is set to {config['loss_limit']}\n")
            no_loss_limit = True
            # making sure the bet is more than 
            while no_loss_limit:
                loss_limit_value = input('reset your loss limit in naira e.g. 1000, if you don"t set your loss limit, if you are unfortunate, the bot might run until you have lost all your funds \n')
                if loss_limit_value.isdecimal():
                    if int(loss_limit_value) >= 200:
                        config['loss_limit'] = loss_limit_value
                        print(f"++++++++++++++++++++\nthe loss limit has been successfully set {loss_limit_value}\n++++++++++++++++++++")
                        no_loss_limit = False
                    else:
                        print('++++++++++++++++++++\nloss limit too small the least should be 200\n++++++++++++++++++++')
                        time.sleep(2)
                else:
                    print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                    time.sleep(2)

          
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                conf.write(write_json)

            time.sleep(2)
            self.__init__()

        elif arg == "profit_limit":
            print(f"\nThe current profit limit is set to {config['profit_limit']}\n")
            no_profit_limit = True
            # making sure the bet is more than 
            while no_profit_limit:
                profit_limit_value = input('reset your profit limit in naira e.g. 1000, if you don"t set your profit limit, you might never make any profit till the bot reach loss limit and if you did not set your loss limit as well you might lose all you funds \n')
                if profit_limit_value.isdecimal():
                    if int(profit_limit_value) >= 200:
                        config['profit_limit'] = profit_limit_value
                        print(f"++++++++++++++++++++\nthe profit limit has been successfully set {profit_limit_value}\n++++++++++++++++++++")
                        no_profit_limit = False
                    else:
                        print('++++++++++++++++++++\nprofit limit too small the least should be 200\n++++++++++++++++++++')
                        time.sleep(2)
                else:
                    print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                    time.sleep(2)

          
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                conf.write(write_json)

            time.sleep(2)
            self.__init__()

        elif arg == "password":
            print(f"\nyour current password is set to {config['password']}\n")
            unconfirmed_password = True
            password = ""
            while unconfirmed_password:
                password_value = getpass(prompt='reset your bet9ja password \n')
                password_value_comfirmed = getpass(prompt='confirm your password\n')
                # password_value = input('reset your bet9ja password \n')
                # password_value_comfirmed = input('confirm your password\n')
                if password_value == password_value_comfirmed:
                    unconfirmed_password = False
                    password = password_value
                    print(f'++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your bet9ja password to {password} \n++++++++++++++++++++')
                else:
                    print('++++++++++++++++++++\nyour password and confirm password must match\n++++++++++++++++++++')
                    time.sleep(2)

            config['password'] = password
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\conf.json', 'w') as conf:
                conf.write(write_json)
            
            time.sleep(2)
            self.__init__()

        elif arg == 'bot_algorithm':
            algo_value = self.ask_for_input('Set your prefered the bot algorithm\n1. This algorithm looks for a color to win two, three times consecutive and play if the color comes once afterward \n2. This algorithm looks for a color to win with 4 colors, then it waits for oppositing colors to play lose for 3 times straight then it plays the 4th time if it is a lose it doubles the stake and play the fifth time.\n3. This algorithm looks for a color to win with 4 colors and any color to be absent i.e. to have 0 color then the bot will play on two colors except that 0 color. \n', 3)
            config['bot_algorithm'] = algo_value
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\conf.json', 'w') as config:
                config.write(write_json)

            time.sleep(2)
            self.__init__()

        elif arg == "alert_music":
            file_path = input('Go to Your preferred sound, copy and paste the file path e.g C:/Users/dataslid/Music/fem.mp3\n')
            config['alert_music'] = file_path
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\conf.json', 'w') as config:
                config.write(write_json)
            
            time.sleep(2) 
            self.__init__()


    def ask_for_input(self, question, max_choice):
        choice = ""
        while choice == "":
            num_input = input(question)
            if num_input.isdecimal():
                choice = int(num_input)
                if choice <= max_choice:
                    return choice
                
                print('++++++++++++++++++++\nyour choice is out of bound\n++++++++++++++++++++')
                choice = ""
            print('++++++++++++++++++++\ninvalid choice\n++++++++++++++++++++')
 
Bot()
    """ % (name, version, remote_url, user_id)

    return bet9ja