import javax.swing.*;
import java.awt.*;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class PhonebookApp extends JFrame {

    // объявляю элементы графического интерфейса
    private JTextField firstNameField;
    private JTextField lastNameField;
    private JTextField phoneField;
    private JTextArea resultArea;

    // настраиваю главное окно, задаю размеры и расположение элементов на экране
    public PhonebookApp() {
        setTitle("Телефонный справочник (крутой)");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(600, 550);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout());

        // создаю верхнюю панель для ввода текста (3 строки по 2 столбца)
        JPanel inputPanel = new JPanel(new GridLayout(3, 2, 5, 5));
        inputPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 5, 10));

        inputPanel.add(new JLabel("Имя:"));
        firstNameField = new JTextField();
        inputPanel.add(firstNameField);

        inputPanel.add(new JLabel("Фамилия:"));
        lastNameField = new JTextField();
        inputPanel.add(lastNameField);

        inputPanel.add(new JLabel("Телефон (для удаления нужен точный):"));
        phoneField = new JTextField();
        inputPanel.add(phoneField);

        add(inputPanel, BorderLayout.NORTH);

        // создаю отдельную панель для кнопок, чтобы они стояли в ряд по центру
        JPanel buttonPanel = new JPanel(new FlowLayout());
        JButton searchButton = new JButton("Найти");
        JButton addButton = new JButton("Добавить");
        JButton deleteButton = new JButton("Удалить");

        buttonPanel.add(searchButton);
        buttonPanel.add(addButton);
        buttonPanel.add(deleteButton);

        // добавляю панель с кнопками чуть ниже полей ввода
        add(buttonPanel, BorderLayout.CENTER);

        // настраиваю текстовое поле для вывода результатов поиска, запрещаю его редактировать руками
        resultArea = new JTextArea();
        resultArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(resultArea);
        scrollPane.setBorder(BorderFactory.createTitledBorder("Результаты:"));
        scrollPane.setPreferredSize(new Dimension(480, 380));
        
        // помещаю результаты в нижнюю часть окна
        add(scrollPane, BorderLayout.SOUTH);

        // привязываю методы к нажатию соответствующих кнопок
        searchButton.addActionListener(e -> performSearch());
        addButton.addActionListener(e -> performAdd());
        deleteButton.addActionListener(e -> performDelete());
    }

    // собираю текст из полей, очищаю от пробелов и прошу репозиторий найти совпадения
    private void performSearch() {
        resultArea.setText("");
        String fName = firstNameField.getText().trim();
        String lName = lastNameField.getText().trim();
        String phone = phoneField.getText().trim();

        // получаю готовые DTO объекты, чтобы интерфейс ничего не знал про сущности БД
        List<ContactDTO> results = ContactRepository.searchContacts(fName, lName, phone);

        if (results.isEmpty()) {
            resultArea.setText("Запись не найдена!");
        } else {
            StringBuilder sb = new StringBuilder();
            for (ContactDTO dto : results) {
                sb.append(dto.toString()).append("\n");
                sb.append("-----------------------------\n");
            }
            resultArea.setText(sb.toString());
        }
    }

    // проверяю, что поля не пустые, и передаю данные в репозиторий для сохранения
    private void performAdd() {
        String fName = firstNameField.getText().trim();
        String lName = lastNameField.getText().trim();
        String phone = phoneField.getText().trim();

        if (fName.isEmpty() || phone.isEmpty()) {
            resultArea.setText("Ошибка: Имя и Телефон обязательны для добавления!");
            return;
        }

        ContactRepository.addContact(fName, lName, phone);
        resultArea.setText("Контакт успешно добавлен: " + fName + " " + lName);
        
        // очищаю поля после успешного добавления
        firstNameField.setText("");
        lastNameField.setText("");
        phoneField.setText("");
    }

    // удаляю запись по указанному номеру телефона, так как он уникален
    private void performDelete() {
        String phone = phoneField.getText().trim();

        if (phone.isEmpty()) {
            resultArea.setText("Ошибка: Введите точный номер телефона для удаления!");
            return;
        }

        boolean success = ContactRepository.deleteContact(phone);
        if (success) {
            resultArea.setText("Контакт с телефоном " + phone + " успешно удален!");
            phoneField.setText("");
        } else {
            resultArea.setText("Ошибка: Контакт с таким телефоном не найден.");
        }
    }

    public static void main(String[] args) {
        // перед запуском окон проверяю БД и создаю таблицы с тестовыми данными
        ContactRepository.initDatabase();

        SwingUtilities.invokeLater(() -> {
            new PhonebookApp().setVisible(true);
        });
    }

    // сущность, которая является точной копией строки из базы данных (включает ID)
    static class ContactEntity {
        public int id;
        public String firstName;
        public String lastName;
        public String phone;

        public ContactEntity(int id, String firstName, String lastName, String phone) {
            this.id = id;
            this.firstName = firstName;
            this.lastName = lastName;
            this.phone = phone;
        }
    }

    // объект передачи данных (DTO), скрывает ID от пользователя и красиво форматирует текст
    static class ContactDTO {
        public String fullName;
        public String formattedPhone;

        public ContactDTO(String fullName, String formattedPhone) {
            this.fullName = fullName;
            this.formattedPhone = formattedPhone;
        }

        @Override
        public String toString() {
            return "Абонент: " + fullName + "\nТел: " + formattedPhone;
        }
    }

    // преобразователь (Mapper), изолирует логику перевода Entity в DTO и обратно
    static class ContactMapper {
        
        // беру сырой ответ из БД (ResultSet) и делаю из него доменную сущность Entity
        public static ContactEntity toEntity(ResultSet rs) throws SQLException {
            return new ContactEntity(
                    rs.getInt("id"),
                    rs.getString("first_name"),
                    rs.getString("last_name"),
                    rs.getString("phone")
            );
        }

        // беру сырые строки от пользователя и собираю сущность Entity перед сохранением в БД
        // id ставлю 0, так как база H2 сама выдаст настоящий ID при вставке
        public static ContactEntity toEntityFromInput(String fName, String lName, String phone) {
            return new ContactEntity(0, fName, lName, phone);
        }

        // перевожу Entity в красивый DTO для вывода на экран, склеивая имя и фамилию
        public static ContactDTO toDTO(ContactEntity entity) {
            String fullName = entity.firstName + " " + entity.lastName;
            String phone = "☎ " + entity.phone;
            return new ContactDTO(fullName, phone);
        }
    }

    // класс репозитория, берет на себя всю работу с SQL-запросами к базе H2
    static class ContactRepository {
        // путь сохранит БД в текущей папке проекта в файл phonebook.mv.db
        private static final String DB_URL = "jdbc:h2:./phonebook";

        // создаю таблицу при первом запуске и заливаю 13 базовых контактов
        public static void initDatabase() {
            try (Connection conn = DriverManager.getConnection(DB_URL);
                 Statement stmt = conn.createStatement()) {
                
                String createTableSql = "CREATE TABLE IF NOT EXISTS contacts (" +
                        "id INT AUTO_INCREMENT PRIMARY KEY," +
                        "first_name VARCHAR(255)," +
                        "last_name VARCHAR(255)," +
                        "phone VARCHAR(50)" +
                        ");";
                stmt.execute(createTableSql);

                // проверяю пустая ли таблица, чтобы не плодить дубли при перезапусках
                ResultSet rs = stmt.executeQuery("SELECT COUNT(*) AS count FROM contacts");
                if (rs.next() && rs.getInt("count") == 0) {
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Иван', 'Иванов', '89991234567')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Петр', 'Петров', '89997654321')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Анна', 'Смирнова', '89990001122')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Алексей', 'Смирнов', '89001112233')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Елена', 'Васильева', '89004445566')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Дмитрий', 'Соколов', '89112223344')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Ольга', 'Михайлова', '89223334455')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Сергей', 'Новиков', '89334445566')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Мария', 'Федорова', '89445556677')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Андрей', 'Морозов', '89556667788')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Наталья', 'Волкова', '89667778899')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Максим', 'Лебедев', '89778889900')");
                    stmt.execute("INSERT INTO contacts (first_name, last_name, phone) VALUES ('Екатерина', 'Егорова', '89889990011')");
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }

        // ищу контакты по подстроке и возвращаю уже готовые DTO через маппер
        public static List<ContactDTO> searchContacts(String firstName, String lastName, String phone) {
            List<ContactDTO> resultList = new ArrayList<>();
            String sql = "SELECT * FROM contacts WHERE first_name LIKE ? AND last_name LIKE ? AND phone LIKE ?";

            try (Connection conn = DriverManager.getConnection(DB_URL);
                 PreparedStatement pstmt = conn.prepareStatement(sql)) {

                pstmt.setString(1, "%" + firstName + "%");
                pstmt.setString(2, "%" + lastName + "%");
                pstmt.setString(3, "%" + phone + "%");

                ResultSet rs = pstmt.executeQuery();

                while (rs.next()) {
                    ContactEntity entity = ContactMapper.toEntity(rs);
                    ContactDTO dto = ContactMapper.toDTO(entity);
                    resultList.add(dto);
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
            return resultList;
        }

        // принимаю данные от интерфейса, через маппер создаю Entity и сохраняю в базу
        public static void addContact(String firstName, String lastName, String phone) {
            ContactEntity newEntity = ContactMapper.toEntityFromInput(firstName, lastName, phone);
            String sql = "INSERT INTO contacts (first_name, last_name, phone) VALUES (?, ?, ?)";

            try (Connection conn = DriverManager.getConnection(DB_URL);
                 PreparedStatement pstmt = conn.prepareStatement(sql)) {

                pstmt.setString(1, newEntity.firstName);
                pstmt.setString(2, newEntity.lastName);
                pstmt.setString(3, newEntity.phone);
                pstmt.executeUpdate();

            } catch (SQLException e) {
                e.printStackTrace();
            }
        }

        // удаляю контакт по конкретному номеру телефона. возвращаю true если удалилось
        public static boolean deleteContact(String phone) {
            String sql = "DELETE FROM contacts WHERE phone = ?";
            try (Connection conn = DriverManager.getConnection(DB_URL);
                 PreparedStatement pstmt = conn.prepareStatement(sql)) {

                pstmt.setString(1, phone);
                // executeUpdate возвращает количество измененных строк
                int affectedRows = pstmt.executeUpdate();
                return affectedRows > 0; 

            } catch (SQLException e) {
                e.printStackTrace();
            }
            return false;
        }
    }
}