from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TicTacToeGameTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.credentials_player1 = {
            'username': 'root',
            'password': '1234'
        }
        self.credentials_player2 = {
            'username': 'root2',
            'password': '1234'
        }
        # Создаем пользователя
        User.objects.create_user(**self.credentials_player1)
        User.objects.create_user(**self.credentials_player2)

    def test_login_redirect(self):
        print("Step 1: Opening login page")
        self.browser.get(self.live_server_url + '/login/')
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        submit_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')

        username_input.send_keys('root')
        password_input.send_keys('1234')
        submit_button.click()

        # Проверяем, что после авторизации происходит перенаправление на главную страницу
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse('index')
        )

    def test_create_and_join_game(self):
        # Первый игрок авторизуется
        print("Step 1: First player login")
        self.browser.get(self.live_server_url + '/login/')
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        submit_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')

        username_input.send_keys('root')
        password_input.send_keys('1234')
        submit_button.click()

        # Первый игрок создает игру
        print("Step 2: First player creates a game")
        self.browser.get(self.live_server_url + '/play-with-human/')
        # Ожидание загрузки формы
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'create-game-form'))
        )
        game_id = self.browser.execute_script(
            "return fetch('/create-game/', {method: 'POST', body: new FormData(document.getElementById('create-game-form')), headers: {'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value}}).then(res => res.json());")[
            'game_id']

        # Второй игрок авторизуется
        print("Step 3: Second player login")
        second_browser = webdriver.Firefox()
        second_browser.get(self.live_server_url + '/login/')
        username_input = second_browser.find_element(By.NAME, 'username')
        password_input = second_browser.find_element(By.NAME, 'password')
        submit_button = second_browser.find_element(By.XPATH, '//button[@type="submit"]')

        username_input.send_keys('root2')
        password_input.send_keys('1234')
        submit_button.click()

        # Второй игрок присоединяется к игре
        second_browser.get(self.live_server_url + f'/join-game/{game_id}/')

        # Проверяем, что после присоединения второго игрока происходит перенаправление на страницу игры
        self.assertEqual(
            second_browser.current_url,
            self.live_server_url + reverse('play_game', kwargs={'game_id': game_id})
        )

        # Закрываем второй браузер
        second_browser.quit()

    def test_game_page_display(self):
        print("Step 1: Logging in")
        self.browser.get(self.live_server_url + '/login/')  # Redirect to the login page
        self.browser.find_element(By.NAME,"username").send_keys('root')
        self.browser.find_element(By.NAME, "password").send_keys('1234')
        self.browser.find_element(By.XPATH, '//button[@type="submit"]').click()

        print("Step 2: Checking game page display")
        self.browser.get(self.live_server_url + '/play-with-human/')
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'create-game-form'))
        )
        game_id = self.browser.execute_script(
            "return fetch('/create-game/', {method: 'POST', body: new FormData(document.getElementById('create-game-form')), headers: {'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value}}).then(res => res.json());")[
            'game_id']
        self.browser.get(self.live_server_url + f'/join-game/{game_id}/')
        header_text = self.browser.find_element(By.TAG_NAME, 'h1').text
        self.assertEqual(header_text, 'Крестики-нолики')

        board = self.browser.find_element(By.CLASS_NAME, 'tic-tac-toe-board')
        self.assertIsNotNone(board)

        player_turn_text = self.browser.find_element(By.CLASS_NAME, 'player-turn').text
        self.assertIn('Ход игрока:', player_turn_text)

    def test_game_play(self):
        print("Step 1: Logging in")
        self.browser.get(self.live_server_url + '/login/')  # Redirect to the login page
        self.browser.find_element(By.NAME,"username").send_keys('root')
        self.browser.find_element(By.NAME, "password").send_keys('1234')
        self.browser.find_element(By.XPATH, '//button[@type="submit"]').click()

        print("Step 2: Playing the game")
        self.browser.get(self.live_server_url + '/play-with-human/')
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'create-game-form'))
        )
        game_id = self.browser.execute_script(
            "return fetch('/create-game/', {method: 'POST', body: new FormData(document.getElementById('create-game-form')), headers: {'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value}}).then(res => res.json());")[
            'game_id']
        self.browser.get(self.live_server_url + f'/join-game/{game_id}/')
        cells = self.browser.find_elements(By.CLASS_NAME, 'cell')

        # Ждем, пока элемент станет кликабельным
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'cell'))
        )

        # Кликаем по элементу
        cells[0].click()

        try:
            WebDriverWait(self.browser, 10).until(
                EC.text_to_be_present_in_element((By.ID, 'current-player'), 'O')
            )
            print("Player turn successfully updated to O")
        except TimeoutException:
            print("Failed to update player turn within the timeout period")
            current_player_text = self.browser.find_element(By.ID, 'current-player').text
            print(f"Current player text: {current_player_text}")

        # Continue the game...

    # def test_player_join_leave(self):
    #     print("Step 1: First player login")
    #     self.browser.get(self.live_server_url + '/login/')  # Redirect to the login page
    #     self.browser.find_element(By.NAME,"username").send_keys('root')
    #     self.browser.find_element(By.NAME, "password").send_keys('1234')
    #     self.browser.find_element(By.XPATH, '//button[@type="submit"]').click()
    #
    #     # Create a new browser instance for the second player
    #     print("Step 2: Second player login")
    #     second_browser = webdriver.Firefox()
    #     second_browser.get(self.live_server_url + '/login/') # Redirect to the login page
    #     second_browser.find_element(By.NAME, "username").send_keys('root2')
    #     second_browser.find_element(By.NAME, "password").send_keys('1234')
    #     second_browser.find_element(By.XPATH, '//button[@type="submit"]').click()
    #     second_browser.get(self.live_server_url + '/play-game/1/')
    #
    #     # Wait for the page to load
    #     WebDriverWait(second_browser, 10).until(
    #         EC.presence_of_element_located((By.CLASS_NAME, 'tic-tac-toe-board'))
    #     )
    #
    #     # Check that the player joined message is displayed
    #     player_join_message_second_browser = WebDriverWait(second_browser, 5).until(
    #         EC.text_to_be_present_in_element((By.ID, 'messages'), 'Player joined the game.')
    #     )
    #
    #     # Close the second browser
    #     second_browser.quit()
    #
    #     # Wait for the player leave message to be displayed
    #     player_leave_message = WebDriverWait(self.browser, 5).until(
    #         EC.text_to_be_present_in_element((By.ID, 'messages'), 'Player left the game.')
    #     )

