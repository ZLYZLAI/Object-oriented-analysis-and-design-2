using System;
using System.Drawing;
using System.Windows.Forms;

namespace PCConfigurator
{
    /// Главный класс приложения, объединяющий логику интерфейса и подбора комплектующих
    /// Без использования паттерна "Строитель" для сравнения
    public class Program : Form
    {
        // Поля для хранения состояния выбора пользователя
        private string selectedType = "";   // Выбранная категория (Игры, Офис, Учеба)
        private string selectedBudget = ""; // Выбранный бюджетный уровень

        // Основные элементы графического интерфейса
        private Label headerLabel;   // Заголовок окна
        private Panel contentPanel;  // Контейнер для динамической смены кнопок и текста

        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            // Запуск цикла обработки сообщений Windows
            Application.Run(new Program());
        }

        public Program()
        {
            // Настройка параметров основного окна приложения
            this.Text = "PC Master Configurator 2026";
            this.Size = new Size(600, 650);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;

            // Инициализация верхней панели (шапки)
            headerLabel = new Label();
            headerLabel.Text = "В игрульки всё играем, да?";
            headerLabel.Font = new Font("Segoe UI", 16, FontStyle.Bold);
            headerLabel.Dock = DockStyle.Top;
            headerLabel.Height = 100; 
            headerLabel.TextAlign = ContentAlignment.MiddleCenter;
            headerLabel.BackColor = Color.FromArgb(240, 240, 240); // Фон
            this.Controls.Add(headerLabel);

            // Инициализация центральной панели для кнопок и результатов
            contentPanel = new Panel();
            contentPanel.Dock = DockStyle.Fill;
            this.Controls.Add(contentPanel);

            // Переход к первому экрану выбора
            ShowWelcomeStep();
        }

        /// Экран выбора назначения компьютера
        private void ShowWelcomeStep()
        {
            contentPanel.Controls.Clear();
            headerLabel.Text = "В игрульки всё играем, да?";

            // Размещаем основные категории
            AddButton("Компьютер для учёбы",150, () => { selectedType = "Study"; ShowBudgetStep(); });
            AddButton("Компьютер для офиса", 210, () => { selectedType = "Office"; ShowBudgetStep(); });
            AddButton("Компьютер для игр", 270, () => { selectedType = "Gaming"; ShowBudgetStep(); });
        }

        /// Экран выбора ценовой категории
        private void ShowBudgetStep()
        {
            contentPanel.Controls.Clear();
            headerLabel.Text = "Раскрывай кошелёк:";

            AddButton("Дешёвый", 150, () => { selectedBudget = "Cheap"; FinishAssembly(); });
            AddButton("Средний", 210, () => { selectedBudget = "Medium"; FinishAssembly(); });
            AddButton("Дорогой", 270, () => { selectedBudget = "Expensive"; FinishAssembly(); });

            AddButton("← Назад", 360, () => ShowWelcomeStep());
        }

        /// Центральный метод логики, где происходит жесткое связывание выбора пользователя с комплектующими.
        /// Здесь сосредоточена вся база данных (ну типо) конфигураций
        private void FinishAssembly()
        {
            contentPanel.Controls.Clear();
            headerLabel.Text = "Ваша сборка:";

            // Технические характеристики
            string cpu = "", gpu = "", mb = "", ram = "", storage = "", cool = "";
            int totalPrice = 0;

            // Обработка логики подбора на основе вложенных условий
            if (selectedType == "Gaming")
            {
                if (selectedBudget == "Cheap") {
                    cpu = "Intel Core i3-12100F OEM";
                    gpu = "NVIDIA GeForce GTX 1650 4GB GDDR6";
                    mb = "MSI PRO H610M-E DDR4";
                    ram = "Kingston FURY Beast Black 8GB DDR4 3200MHz";
                    storage = "512GB ADATA XPG SX8200 Pro M.2 NVMe";
                    cool = "DeepCool AG300 (150W)";
                    totalPrice = 48500;
                }
                else if (selectedBudget == "Medium") {
                    cpu = "Intel Core i5-13400F OEM";
                    gpu = "NVIDIA GeForce RTX 4060 Ti 8GB Dual Fan";
                    mb = "GIGABYTE B760M DS3H AX DDR4";
                    ram = "Kingston FURY Renegade 16GB (2x8GB) DDR5 6000MHz";
                    storage = "1TB Samsung 980 Pro MZ-V8P1T0BW";
                    cool = "ID-COOLING SE-224-XTS Black";
                    totalPrice = 118000;
                }
                else {
                    cpu = "Intel Core i9-14900K BOX (без кулера)";
                    gpu = "NVIDIA GeForce RTX 4090 24GB Founders Edition";
                    mb = "ASUS ROG MAXIMUS Z790 HERO";
                    ram = "G.Skill TRIDENT Z5 RGB 64GB (2x32GB) DDR5 6400MHz";
                    storage = "2TB Samsung 990 Pro NVMe Gen4";
                    cool = "СЖО LIAN LI Galahad II LCD 360 Performance";
                    totalPrice = 435000;
                }
            }
            else if (selectedType == "Office")
            {
                if (selectedBudget == "Cheap") {
                    cpu = "Intel Pentium Gold G7400 OEM";
                    gpu = "Интегрированное ядро Intel UHD Graphics 710";
                    mb = "ASUS PRIME H610M-K D4";
                    ram = "Crucial 4GB DDR4 3200MHz CL22";
                    storage = "120GB Kingston A400 SATA III";
                    cool = "Intel Stock Cooler LAMINAR RS1";
                    totalPrice = 21500;
                }
                else if (selectedBudget == "Medium") {
                    cpu = "Intel Core i3-12100 OEM";
                    gpu = "Интегрированное ядро Intel UHD Graphics 730";
                    mb = "MSI PRO B760M-P DDR4";
                    ram = "Crucial 8GB DDR4 3200MHz CL22";
                    storage = "250GB Samsung 970 EVO Plus M.2";
                    cool = "DeepCool Theta 20 PWM";
                    totalPrice = 37000;
                }
                else {
                    cpu = "Intel Core i5-13500 OEM";
                    gpu = "Интегрированное ядро Intel UHD Graphics 770";
                    mb = "ASUS PRIME B760-PLUS DDR5";
                    ram = "Kingston FURY Beast 16GB DDR5 5200MHz";
                    storage = "500GB Samsung 980 NVMe M.2";
                    cool = "be quiet! PURE ROCK 2 Black (150W TDP)";
                    totalPrice = 64000;
                }
            }
            else // Учёба
            {
                if (selectedBudget == "Cheap") {
                    cpu = "AMD Ryzen 3 3200G OEM";
                    gpu = "Интегрированная графика AMD Radeon Vega 8";
                    mb = "ASRock A320M-HDV R4.0";
                    ram = "AMD Radeon R7 Performance 8GB DDR4 2666MHz";
                    storage = "240GB WD Green SATA SSD";
                    cool = "AMD Stock Cooler Wraith Stealth";
                    totalPrice = 26000;
                }
                else if (selectedBudget == "Medium") {
                    cpu = "AMD Ryzen 5 5600G OEM";
                    gpu = "Интегрированная графика AMD Radeon Vega 7";
                    mb = "GIGABYTE B450M K (rev. 1.0)";
                    ram = "Kingston FURY Beast Black 16GB (2x8GB) DDR4 3200MHz";
                    storage = "500GB Kingston NV2 NVMe PCIe 4.0";
                    cool = "DeepCool GAMMAXX 400 V2 Blue";
                    totalPrice = 46500;
                }
                else {
                    cpu = "AMD Ryzen 7 5700G OEM";
                    gpu = "Интегрированная графика AMD Radeon Vega 8";
                    mb = "ASUS TUF GAMING B550-PLUS";
                    ram = "Kingston FURY Renegade 32GB (2x16GB) DDR4 3600MHz";
                    storage = "1TB Samsung 980 NVMe M.2";
                    cool = "be quiet! Shadow Rock 3 (190W TDP)";
                    totalPrice = 78000;
                }
            }

            // Формирование отчета
            Label resultLabel = new Label();
            resultLabel.Text = $"Процессор: {cpu}\n\n" +
                               $"Видеокарта: {gpu}\n\n" +
                               $"Материнская плата: {mb}\n\n" +
                               $"Оперативная память: {ram}\n\n" +
                               $"Накопитель: {storage}\n\n" +
                               $"Охлаждение: {cool}\n\n" +
                               "------------------------------------------------------------------------------------------\n" +
                               $"ИТОГО: {totalPrice:N0} руб.";
            
            resultLabel.AutoSize = true;
            resultLabel.Location = new Point(40, 130); // Отступ внутри панели результата
            resultLabel.Font = new Font("Segoe UI", 10);
            contentPanel.Controls.Add(resultLabel);

            // Кнопка для возврата в начало
            AddButton("Собрать другой ПК", 420, () => ShowWelcomeStep());
        }

        /// Универсальный метод для создания и размещения кнопок на панели.
        /// <param name="text">Текст на кнопке</param>
        /// <param name="top">Позиция по вертикали относительно родительского контейнера</param>
        /// <param name="onClick">Действие, выполняемое при нажатии</param>
        private void AddButton(string text, int top, Action onClick)
        {
            Button btn = new Button();
            btn.Text = text;
            btn.Width = 320; 
            btn.Height = 50;
            btn.Left = (this.ClientSize.Width - btn.Width) / 2; // Динамическая центровка
            btn.Top = top;
            btn.Font = new Font("Segoe UI", 11);
            btn.Cursor = Cursors.Hand;
            
            // Подписка на событие клика через лямбда-выражение
            btn.Click += (s, e) => onClick();
            contentPanel.Controls.Add(btn);
        }
    }
}