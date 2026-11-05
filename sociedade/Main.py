import os, sys, ctypes
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget,
    QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QMessageBox, QToolBar, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from db import (
    criar_usuario, login_usuario, get_usuario, criar_post,
    get_feed, curtir_post, get_post_usuario,
    verificar_amizade, adicionar_amigo
)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rede Social – PyQt6 + MongoDB")
        self.resize(750, 550)
        self.current_user = None
        self.current_post = None
        self.todos_posts = []

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.criar_tela_login()
        self.criar_tela_feed()
        self.criar_tela_post()
        self.criar_tela_perfil()

    def criar_tela_login(self):
        login_w = QWidget()
        lay = QVBoxLayout(login_w)
        lay.setContentsMargins(70, 70, 70, 70)
        lay.setSpacing(12)

        titulo = QLabel("Login")
        titulo.setStyleSheet("font-size: 26px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.usuario_in = QLineEdit()
        self.usuario_in.setPlaceholderText("Usuário")

        self.senha_in = QLineEdit()
        self.senha_in.setPlaceholderText("Senha")
        self.senha_in.setEchoMode(QLineEdit.EchoMode.Password)

        btn_login = QPushButton("Entrar")
        btn_login.clicked.connect(self.fazer_login)

        btn_reg = QPushButton("Cadastrar")
        btn_reg.clicked.connect(self.fazer_cadastro)

        lay.addWidget(titulo)
        lay.addWidget(self.usuario_in)
        lay.addWidget(self.senha_in)
        lay.addWidget(btn_login)
        lay.addWidget(btn_reg)

        self.stack.addWidget(login_w)

    def criar_tela_feed(self):
        feed_w = QWidget()
        flay = QVBoxLayout(feed_w)
        flay.setContentsMargins(0, 0, 0, 12)
        flay.setSpacing(10)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        self.btn_perfil = QPushButton("Perfil")
        self.btn_perfil.clicked.connect(lambda: self.abrir_perfil(self.current_user))

        self.btn_sair = QPushButton("Sair")
        self.btn_sair.clicked.connect(self.sair_da_conta)

        self.busca_in = QLineEdit()
        self.busca_in.setPlaceholderText("🔍 Pesquisar posts...")
        self.busca_in.setClearButtonEnabled(True)
        self.busca_in.setMinimumWidth(280)
        self.busca_in.textChanged.connect(self.filtrar_feed)

        toolbar.addWidget(self.btn_perfil)
        toolbar.addWidget(self.btn_sair)
        toolbar.addWidget(self.busca_in)

        conteudo = QWidget()
        clay = QVBoxLayout(conteudo)
        clay.setContentsMargins(16, 16, 16, 0)
        clay.setSpacing(10)

        self.feed_titulo = QLabel("Feed")
        self.feed_titulo.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.feed_lista = QListWidget()
        self.feed_lista.itemClicked.connect(self.abrir_post)
        self.feed_lista.setAlternatingRowColors(True)
        self.feed_lista.setStyleSheet("""
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background-color: #dbeafe;
                color: black;
            }
        """)

        self.post_texto = QTextEdit()
        self.post_texto.setPlaceholderText("Escreva um post...")
        self.post_texto.setMaximumHeight(90)

        btn_post = QPushButton("Publicar")
        btn_post.clicked.connect(self.fazer_post)

        clay.addWidget(self.feed_titulo)
        clay.addWidget(self.feed_lista, 1)
        clay.addWidget(self.post_texto)
        clay.addWidget(btn_post)

        flay.addWidget(conteudo)
        self.stack.addWidget(feed_w)

    def criar_tela_post(self):
        post_w = QWidget()
        play = QVBoxLayout(post_w)
        play.setContentsMargins(24, 24, 24, 24)
        play.setSpacing(16)

        btn_voltar = QPushButton("← Voltar ao feed")
        btn_voltar.clicked.connect(self.voltar_feed)

        self.post_autor = QLabel("")
        self.post_autor.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.btn_ver_perfil = QPushButton("Ver perfil do autor")
        self.btn_ver_perfil.clicked.connect(self.ver_perfil_do_post)

        self.post_conteudo = QLabel("")
        self.post_conteudo.setWordWrap(True)
        self.post_conteudo.setStyleSheet("""
            font-size: 16px;
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 16px;
        """)

        self.post_likes = QLabel("")
        self.post_likes.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.btn_curtir = QPushButton("❤️ Curtir")
        self.btn_curtir.clicked.connect(self.curtir_post_atual)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.post_conteudo)

        play.addWidget(btn_voltar)
        play.addWidget(self.post_autor)
        play.addWidget(self.btn_ver_perfil)
        play.addWidget(scroll, 1)
        play.addWidget(self.post_likes)
        play.addWidget(self.btn_curtir)

        self.stack.addWidget(post_w)

    def criar_tela_perfil(self):
        perfil_w = QWidget()
        play = QVBoxLayout(perfil_w)
        play.setContentsMargins(24, 24, 24, 24)
        play.setSpacing(14)

        btn_voltar = QPushButton("← Voltar")
        btn_voltar.clicked.connect(self.voltar_para_tela_anterior)

        self.perfil_nome = QLabel("")
        self.perfil_nome.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        self.perfil_info = QLabel("")
        self.perfil_info.setStyleSheet("""
            font-size: 14px;
            color: #475569;
        """)

        self.btn_add_amigo = QPushButton("➕ Adicionar amigo")
        self.btn_add_amigo.clicked.connect(self.adicionar_amigo_atual)

        self.perfil_posts = QListWidget()
        self.perfil_posts.itemClicked.connect(self.abrir_post_do_perfil)
        self.perfil_posts.setAlternatingRowColors(True)
        self.perfil_posts.setStyleSheet("""
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background-color: #dbeafe;
                color: black;
            }
        """)

        play.addWidget(btn_voltar)
        play.addWidget(self.perfil_nome)
        play.addWidget(self.perfil_info)
        play.addWidget(self.btn_add_amigo)
        play.addWidget(QLabel("Publicações"))
        play.addWidget(self.perfil_posts, 1)

        self.stack.addWidget(perfil_w)


    def fazer_cadastro(self):
        u = self.usuario_in.text().strip()
        s = self.senha_in.text()

        if not u or not s:
            QMessageBox.warning(self, "Atenção", "Preencha usuário e senha.")
            return

        try:
            if criar_usuario(u, s):
                self.fazer_login()
            else:
                QMessageBox.warning(
                    self, "Erro",
                    "Esse usuário já existe na sociedade, tente outro."
                )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao cadastrar: {e}")

    def fazer_login(self):
        u = self.usuario_in.text().strip()
        s = self.senha_in.text()

        if not u or not s:
            QMessageBox.warning(
                self, "Atenção",
                "Informe o usuário e senha cadastrados nesta plataforma."
            )
            return

        try:
            user = login_usuario(u, s)
            if user:
                self.current_user = user["usuario"]
                self.atualizar_feed()
                self.stack.setCurrentIndex(1)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao entrar na conta: {e}")

    def fazer_post(self):
        texto = self.post_texto.toPlainText().strip()

        if not texto:
            QMessageBox.warning(
                self, "Atenção",
                "Digite alguma coisa antes de publicar."
            )
            return

        try:
            criar_post(self.current_user, texto)
            self.post_texto.clear()
            self.atualizar_feed()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao publicar: {e}")

    def atualizar_feed(self):
        try:
            self.todos_posts = get_feed()
            self.filtrar_feed()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar feed: {e}")

    def filtrar_feed(self):
        self.feed_lista.clear()
        termo = self.busca_in.text().strip().lower()

        for post in self.todos_posts:
            texto_post = f"@{post['autor']}: {post['texto']}"
            likes = len(post.get("likes", []))

            if termo and termo not in texto_post.lower():
                continue

            item = QListWidgetItem(f"{texto_post}\n❤️ {likes} curtida(s)")
            item.setData(Qt.ItemDataRole.UserRole, str(post["_id"]))
            item.setData(Qt.ItemDataRole.ToolTipRole, post["autor"])
            self.feed_lista.addItem(item)

    def abrir_post(self, item: QListWidgetItem):
        post_id = item.data(Qt.ItemDataRole.UserRole)

        for post in self.todos_posts:
            if str(post["_id"]) == post_id:
                self.current_post = post
                self.mostrar_post(post)
                self.stack.setCurrentIndex(2)
                return

    def mostrar_post(self, post):
        likes = post.get("likes", [])
        ja_curtiu = self.current_user in likes

        self.post_autor.setText(f"@{post['autor']}")
        self.post_conteudo.setText(post["texto"])
        self.post_likes.setText(f"❤️ {len(likes)} curtida(s)")

        if ja_curtiu:
            self.btn_curtir.setText("💔 Remover curtida")
        else:
            self.btn_curtir.setText("❤️ Curtir")

    def curtir_post_atual(self):
        if not self.current_post:
            return

        try:
            post_id = self.current_post["_id"]
            curtir_post(post_id, self.current_user)

            self.atualizar_feed()

            # Atualiza o post aberto com os dados mais recentes
            for post in self.todos_posts:
                if str(post["_id"]) == str(post_id):
                    self.current_post = post
                    self.mostrar_post(post)
                    break

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao curtir post: {e}")

    def ver_perfil_do_post(self):
        if self.current_post:
            self.abrir_perfil(self.current_post["autor"])

    def voltar_feed(self):
        self.atualizar_feed()
        self.stack.setCurrentIndex(1)

    def abrir_perfil(self, usuario):
        if not usuario:
            return

        try:
            user = get_usuario(usuario)

            if not user:
                QMessageBox.warning(self, "Erro", "Usuário não encontrado.")
                return

            self.perfil_atual = usuario
            self.tela_anterior = self.stack.currentIndex()

            posts = get_post_usuario(usuario)
            amigos = user.get("amigos", [])

            self.perfil_nome.setText(f"@{usuario}")
            self.perfil_info.setText(
                f"{len(posts)} publicação(ões) • {len(amigos)} amigo(s)"
            )

            self.perfil_posts.clear()

            if not posts:
                self.perfil_posts.addItem("Este usuário ainda não publicou nada.")
            else:
                for post in posts:
                    likes = len(post.get("likes", []))
                    item = QListWidgetItem(
                        f"{post['texto']}\n❤️ {likes} curtida(s)"
                    )
                    item.setData(Qt.ItemDataRole.UserRole, str(post["_id"]))
                    self.perfil_posts.addItem(item)

            # Configura o botão de amizade
            if usuario == self.current_user:
                self.btn_add_amigo.setText("Este é seu perfil")
                self.btn_add_amigo.setEnabled(False)
            elif verificar_amizade(self.current_user, usuario):
                self.btn_add_amigo.setText("✅ Já são amigos")
                self.btn_add_amigo.setEnabled(False)
            else:
                self.btn_add_amigo.setText("➕ Adicionar amigo")
                self.btn_add_amigo.setEnabled(True)

            self.stack.setCurrentIndex(3)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir perfil: {e}")


    def adicionar_amigo_atual(self):
        if not self.perfil_atual or not self.current_user:
            return

        try:
            adicionar_amigo(self.current_user, self.perfil_atual)
            QMessageBox.information(
                self,
                "Amigos",
                f"@{self.perfil_atual} foi adicionado aos seus amigos."
            )
            self.abrir_perfil(self.perfil_atual)

        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))


    def abrir_post_do_perfil(self, item: QListWidgetItem):
        post_id = item.data(Qt.ItemDataRole.UserRole)

        if not post_id:
            return

        for post in self.todos_posts:
            if str(post["_id"]) == post_id:
                self.current_post = post
                self.mostrar_post(post)
                self.stack.setCurrentIndex(2)
                return

        # Se o post não estiver no feed carregado, busca pelo autor
        try:
            posts_autor = get_post_usuario(self.perfil_atual)

            for post in posts_autor:
                if str(post["_id"]) == post_id:
                    self.current_post = post
                    self.mostrar_post(post)
                    self.stack.setCurrentIndex(2)
                    return

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir post: {e}")


    def voltar_para_tela_anterior(self):
        if self.tela_anterior == 2:
            self.stack.setCurrentIndex(2)
        else:
            self.atualizar_feed()
            self.stack.setCurrentIndex(1)

    def sair_da_conta(self):
        resposta = QMessageBox.question(
            self,
            "Sair da conta",
            "Deseja realmente sair da sua conta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if resposta == QMessageBox.StandardButton.Yes:
            self.current_user = None
            self.current_post = None
            self.usuario_in.clear()
            self.senha_in.clear()
            self.post_texto.clear()
            self.busca_in.clear()
            self.feed_lista.clear()
            self.stack.setCurrentIndex(0)


if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Sociedade.PyQt6.App")
    app = QApplication(sys.argv)

    caminho_icone = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "icon.ico"
    )

    icone = QIcon(caminho_icone)
    app.setWindowIcon(icone)

    win = App()
    win.setWindowIcon(icone)
    win.show()

    sys.exit(app.exec())