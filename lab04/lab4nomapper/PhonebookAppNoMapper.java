import javax.swing.*;
import java.awt.*;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class PhonebookAppNoMapper extends JFrame {

    // объявляю элементы интерфейса
    private JTextField firstNameField;
    private JTextField lastNameField;
    private JTextField phoneField;
    private JTextArea resultArea;

    // настраиваю окно
    public PhonebookAppNoMapper() {
        setTitle("Телефонный справочник (Без Mapper)");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(600, 550);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout());

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

        JPanel buttonPanel = new JPanel(new FlowLayout());
        JButton searchButton = new JButton("Найти");
        JButton addButton = new JButton("Добавить");
        JButton deleteButton = new JButton("Удалить");

        buttonPanel.add(searchButton);
        buttonPanel.add(addButton);
        buttonPanel.add(deleteButton);

        add(buttonPanel, BorderLayout.CENTER);

        resultArea = new JTextArea();
        resultArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(resultArea);
        scrollPane.setBorder(BorderFactory.createTitledBorder("Результаты:"));
        scrollPane.setPreferredSize(new Dimension(480, 380));
        
        add(scrollPane, BorderLayout.SOUTH);

        searchButton.addActionListener(e -> performSearch());
        addButton.addActionListener(e -> performAdd());
        deleteButton.addActionListener(e -> performDelete());
    }

    // собираю текст и ищу. тут же сам форматирую вывод (что нарушает архитектуру, т.к. gui лезет в логику)
    private void performSearch() {
        resultArea.setText("");
        String fName = firstNameField.getText().trim();
        String lName = lastNameField.getText().trim();
        String phone = phoneField.getText().trim();

        // получаю сырые объекты прямо из базы данных (вместе с id, который мне тут не нужен)
        List<Contact> results = ContactRepository.searchContacts(fName, lName, phone);

        if (results.isEmpty()) {
            resultArea.setText("Запись не найдена!");
        } else {
            StringBuilder sb = new StringBuilder();
            for (Contact contact : results) {
                // интерфейс сам склеивает строки и добавляет значки. это плохо
                String fullName = contact.firstName + " " + contact.lastName;
                String formattedPhone = "☎ " + contact.phone;
                
                sb.append("Абонент: ").append(fullName).append("\n");
                sb.append("Тел: ").append(formattedPhone).append("\n");
                sb.append("-----------------------------\n");
            }
            resultArea.setText(sb.toString());
        }
    }

    // добавляю контакт напрямую передавая строки в репозиторий
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
        
        firstNameField.setText("");
        lastNameField.setText("");
        phoneField.setText("");
    }

    // удаляю контакт по телефону
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
        ContactRepository.initDatabase();
        SwingUtilities.invokeLater(() -> {
            new PhonebookAppNoMapper().setVisible(true);
        });
    }

    // единая модель данных. используется и для БД, и для графического интерфейса
    static class Contact {
        public int id;
        public String firstName;
        public String lastName;
        public String phone;

        public Contact(int id, String firstName, String lastName, String phone) {
            this.id = id;
            this.firstName = firstName;
            this.lastName = lastName;
            this.phone = phone;
        }
    }

    // репозиторий берет на себя не только sql, но и сборку объектов (смешивание ответственностей)
    static class ContactRepository {
        private static final String DB_URL = "jdbc:h2:./phonebook";

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

        // метод возвращает единую модель Contact напрямую
        public static List<Contact> searchContacts(String firstName, String lastName, String phone) {
            List<Contact> resultList = new ArrayList<>();
            String sql = "SELECT * FROM contacts WHERE first_name LIKE ? AND last_name LIKE ? AND phone LIKE ?";

            try (Connection conn = DriverManager.getConnection(DB_URL);
                 PreparedStatement pstmt = conn.prepareStatement(sql)) {

                pstmt.setString(1, "%" + firstName + "%");
                pstmt.setString(2, "%" + lastName + "%");
                pstmt.setString(3, "%" + phone + "%");

                ResultSet rs = pstmt.executeQuery();

                // репозиторий сам парсит базу, без помощи маппера
                while (rs.next()) {
                    Contact contact = new Contact(
                            rs.getInt("id"),
                            rs.getString("first_name"),
                            rs.getString("last_name"),
                            rs.getString("phone")
                    );
                    resultList.add(contact);
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
            return resultList;
        }

        public static void addContact(String firstName, String lastName, String phone) {
            String sql = "INSERT INTO contacts (first_name, last_name, phone) VALUES (?, ?, ?)";
            try (Connection conn = DriverManager.getConnection(DB_URL);
                 PreparedStatement pstmt = conn.prepareStatement(sql)) {

                pstmt.setString(1, firstName);
                pstmt.setString(2, lastName);
                pstmt.setString(3, phone);
                pstmt.executeUpdate();

            } catch (SQLException e) {
                e.printStackTrace();
            }
        }

        public static boolean deleteContact(String phone) {
            String sql = "DELETE FROM contacts WHERE phone = ?";
            try (Connection conn = DriverManager.getConnection(DB_URL);
                 PreparedStatement pstmt = conn.prepareStatement(sql)) {

                pstmt.setString(1, phone);
                return pstmt.executeUpdate() > 0; 

            } catch (SQLException e) {
                e.printStackTrace();
            }
            return false;
        }
    }
}