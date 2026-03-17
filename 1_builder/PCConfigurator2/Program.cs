#nullable disable
using System;
using System.Drawing;
using System.Windows.Forms;
using System.Collections.Generic;

namespace PCConfigurator2Builder
{
    // 1. ПРОДУКТ (КЛАСС ОБЪЕКТА)

    /// Представляет конечный результат сборки - сложный объект "Компьютер".
    /// Содержит только данные о компонентах и не знает, как они подбирались.
    public class Computer
    {
        public string CPU { get; set; }
        public string GPU { get; set; }
        public string Motherboard { get; set; }
        public string RAM { get; set; }
        public string Storage { get; set; }
        public string Cooling { get; set; }
        public int TotalPrice { get; set; }

        /// Возвращает текстовое описание всех характеристик сборки.
        public string GetDescription()
        {
            return $"Процессор: {CPU}\n\n" +
                   $"Видеокарта: {gpuName(GPU)}\n\n" +
                   $"Материнская плата: {Motherboard}\n\n" +
                   $"Оперативная память: {RAM}\n\n" +
                   $"Накопитель: {Storage}\n\n" +
                   $"Охлаждение: {Cooling}\n\n" +
                   "------------------------------------------------------------------------------------------\n" +
                   $"ИТОГО К ОПЛАТЕ: {TotalPrice:N0} руб.";
        }

        private string gpuName(string name) => string.IsNullOrEmpty(name) ? "Интегрированное графическое ядро" : name;
    }

    // 2. ИНТЕРФЕЙС СТРОИТЕЛЯ

    /// Интерфейс строителя определяет шаги, необходимые для создания продукта.
    /// Каждый конкретный строитель будет реализовывать эти шаги по-своему.
    public interface IPCBuilder
    {
        void SetCPU(string budget);
        void SetGPU(string budget);
        void SetMotherboard(string budget);
        void SetRAM(string budget);
        void SetStorage(string budget);
        void SetCooling(string budget);
        void CalculatePrice(string budget);
        Computer GetResult();
    }

    // 3. КОНКРЕТНЫЕ СТРОИТЕЛИ

    /// Строитель для игровых конфигураций.
    public class GamingBuilder : IPCBuilder
    {
        private Computer _pc = new Computer();

        public void SetCPU(string budget) => _pc.CPU = budget == "Cheap" ? "Intel Core i3-12100F OEM" : budget == "Medium" ? "Intel Core i5-13400F OEM" : "Intel Core i9-14900K BOX (без кулера)";
        public void SetGPU(string budget) => _pc.GPU = budget == "Cheap" ? "NVIDIA GeForce GTX 1650 4GB GDDR6" : budget == "Medium" ? "NVIDIA GeForce RTX 4060 Ti 8GB Dual Fan" : "NVIDIA GeForce RTX 4090 24GB Founders Edition";
        public void SetMotherboard(string budget) => _pc.Motherboard = budget == "Cheap" ? "MSI PRO H610M-E DDR4" : budget == "Medium" ? "GIGABYTE B760M DS3H AX DDR4" : "ASUS ROG MAXIMUS Z790 HERO";
        public void SetRAM(string budget) => _pc.RAM = budget == "Cheap" ? "Kingston FURY Beast Black 8GB DDR4 3200MHz" : budget == "Medium" ? "Kingston FURY Renegade 16GB (2x8GB) DDR5 6000MHz" : "G.Skill TRIDENT Z5 RGB 64GB (2x32GB) DDR5 6400MHz";
        public void SetStorage(string budget) => _pc.Storage = budget == "Cheap" ? "512GB ADATA XPG SX8200 Pro M.2 NVMe" : budget == "Medium" ? "1TB Samsung 980 Pro MZ-V8P1T0BW" : "2TB Samsung 990 Pro NVMe Gen4";
        public void SetCooling(string budget) => _pc.Cooling = budget == "Cheap" ? "DeepCool AG300 (150W)" : budget == "Medium" ? "ID-COOLING SE-224-XTS Black" : "СЖО LIAN LI Galahad II LCD 360 Performance";
        public void CalculatePrice(string budget) => _pc.TotalPrice = budget == "Cheap" ? 48500 : budget == "Medium" ? 118000 : 435000;
        public Computer GetResult() => _pc;
    }

    /// Строитель для учебных конфигураций.
    public class StudyBuilder : IPCBuilder
    {
        private Computer _pc = new Computer();

        public void SetCPU(string budget) => _pc.CPU = budget == "Cheap" ? "AMD Ryzen 3 3200G OEM" : budget == "Medium" ? "AMD Ryzen 5 5600G OEM" : "AMD Ryzen 7 5700G OEM";
        public void SetGPU(string budget) => _pc.GPU = budget == "Cheap" ? "AMD Radeon Vega 8" : budget == "Medium" ? "AMD Radeon Vega 7" : "AMD Radeon Vega 8 High End";
        public void SetMotherboard(string budget) => _pc.Motherboard = budget == "Cheap" ? "ASRock A320M-HDV R4.0" : budget == "Medium" ? "GIGABYTE B450M K (rev. 1.0)" : "ASUS TUF GAMING B550-PLUS";
        public void SetRAM(string budget) => _pc.RAM = budget == "Cheap" ? "AMD Radeon R7 Performance 8GB DDR4 2666MHz" : budget == "Medium" ? "Kingston FURY Beast Black 16GB (2x8GB) DDR4 3200MHz" : "Kingston FURY Renegade 32GB (2x16GB) DDR4 3600MHz";
        public void SetStorage(string budget) => _pc.Storage = budget == "Cheap" ? "240GB WD Green SATA SSD" : budget == "Medium" ? "500GB Kingston NV2 NVMe PCIe 4.0" : "1TB Samsung 980 NVMe M.2";
        public void SetCooling(string budget) => _pc.Cooling = budget == "Cheap" ? "AMD Stock Cooler Wraith Stealth" : budget == "Medium" ? "DeepCool GAMMAXX 400 V2 Blue" : "be quiet! Shadow Rock 3 (190W TDP)";
        public void CalculatePrice(string budget) => _pc.TotalPrice = budget == "Cheap" ? 26000 : budget == "Medium" ? 46500 : 78000;
        public Computer GetResult() => _pc;
    }

    /// Строитель для офисных конфигураций.
    public class OfficeBuilder : IPCBuilder
    {
        private Computer _pc = new Computer();

        public void SetCPU(string budget) => _pc.CPU = budget == "Cheap" ? "Intel Pentium Gold G7400 OEM" : budget == "Medium" ? "Intel Core i3-12100 OEM" : "Intel Core i5-13500 OEM";
        public void SetGPU(string budget) => _pc.GPU = budget == "Cheap" ? "Intel UHD Graphics 710" : budget == "Medium" ? "Intel UHD Graphics 730" : "Intel UHD Graphics 770";
        public void SetMotherboard(string budget) => _pc.Motherboard = budget == "Cheap" ? "ASUS PRIME H610M-K D4" : budget == "Medium" ? "MSI PRO B760M-P DDR4" : "ASUS PRIME B760-PLUS DDR5";
        public void SetRAM(string budget) => _pc.RAM = budget == "Cheap" ? "Crucial 4GB DDR4 3200MHz CL22" : budget == "Medium" ? "Crucial 8GB DDR4 3200MHz CL22" : "Kingston FURY Beast 16GB DDR5 5200MHz";
        public void SetStorage(string budget) => _pc.Storage = budget == "Cheap" ? "120GB Kingston A400 SATA III" : budget == "Medium" ? "250GB Samsung 970 EVO Plus M.2" : "500GB Samsung 980 NVMe M.2";
        public void SetCooling(string budget) => _pc.Cooling = budget == "Cheap" ? "Intel Stock Cooler LAMINAR RS1" : budget == "Medium" ? "DeepCool Theta 20 PWM" : "be quiet! PURE ROCK 2 Black (150W TDP)";
        public void CalculatePrice(string budget) => _pc.TotalPrice = budget == "Cheap" ? 21500 : budget == "Medium" ? 37000 : 64000;
        public Computer GetResult() => _pc;
    }

    // 4. ДИРЕКТОР 

    /// Директор отвечает за последовательность вызовов строителя.
    /// Он знает "алгоритм сборки", но не знает, какие именно детали ставятся.
    public class Director
    {
        public void ConstructPC(IPCBuilder builder, string budget)
        {
            builder.SetCPU(budget);
            builder.SetGPU(budget);
            builder.SetMotherboard(budget);
            builder.SetRAM(budget);
            builder.SetStorage(budget);
            builder.SetCooling(budget);
            builder.CalculatePrice(budget);
        }
    }

    // 5. ГРАФИЧЕСКИЙ ИНТЕРФЕЙС

    public class Program : Form
    {
        private IPCBuilder currentBuilder; // Храним интерфейс, а не конкретный класс
        private Director director = new Director();

        private Label headerLabel;
        private Panel contentPanel;

        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.Run(new Program());
        }

        public Program()
        {
            this.Text = "PC Builder Pattern 2026";
            this.Size = new Size(600, 650);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedSingle;

            headerLabel = new Label();
            headerLabel.Font = new Font("Segoe UI", 16, FontStyle.Bold);
            headerLabel.Dock = DockStyle.Top;
            headerLabel.Height = 120;
            headerLabel.TextAlign = ContentAlignment.MiddleCenter;
            this.Controls.Add(headerLabel);

            contentPanel = new Panel();
            contentPanel.Dock = DockStyle.Fill;
            this.Controls.Add(contentPanel);

            ShowWelcomeStep();
        }

        private void ShowWelcomeStep()
        {
            contentPanel.Controls.Clear();
            headerLabel.Text = "В игрульки всё играем, да?";

            // Здесь мы выбираем, какого строителя использовать
            AddButton("Компьютер для учёбы", 150, () => { currentBuilder = new StudyBuilder(); ShowBudgetStep(); });
            AddButton("Компьютер для офиса", 210, () => { currentBuilder = new OfficeBuilder(); ShowBudgetStep(); });
            AddButton("Компьютер для игр", 270, () => { currentBuilder = new GamingBuilder(); ShowBudgetStep(); });
        }

        private void ShowBudgetStep()
        {
            contentPanel.Controls.Clear();
            headerLabel.Text = "Раскрывай кошелёк:";

            AddButton("Дешёвый", 150, () => FinishAssembly("Cheap"));
            AddButton("Средний", 210, () => FinishAssembly("Medium"));
            AddButton("Дорогой", 270, () => FinishAssembly("Expensive"));
            AddButton("← Назад", 360, () => ShowWelcomeStep());
        }

        private void FinishAssembly(string budget)
        {
            contentPanel.Controls.Clear();
            headerLabel.Text = "Ваша сборка:";

            // Директор собирает ПК, используя выбранного ранее строителя
            director.ConstructPC(currentBuilder, budget);
            Computer finalPC = currentBuilder.GetResult();

            Label resultLabel = new Label();
            resultLabel.Text = finalPC.GetDescription();
            resultLabel.AutoSize = true;
            resultLabel.Location = new Point(40, 130);
            resultLabel.Font = new Font("Segoe UI", 10);
            contentPanel.Controls.Add(resultLabel);

            AddButton("Собрать другой ПК", 420, () => ShowWelcomeStep());
        }

        private void AddButton(string text, int top, Action onClick)
        {
            Button btn = new Button { Text = text, Width = 320, Height = 50, Top = top };
            btn.Left = (this.ClientSize.Width - btn.Width) / 2;
            btn.Font = new Font("Segoe UI", 11);
            btn.Click += (s, e) => onClick();
            contentPanel.Controls.Add(btn);
        }
    }
}