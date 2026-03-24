#include <SFML/Graphics.hpp>
#include <nlohmann/json.hpp>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>
#include <memory>
#include <windows.h> 
#include <filesystem>

using namespace std;

using json = nlohmann::json;

// это приспособленец
// здесь хранится тяжелая информация, которая одинакова для всех объектов одного типа
struct ObjectType {
    wstring name;
    string filename;
    sf::Texture texture;

    ObjectType(const wstring& n, const string& file) : name(n), filename(file) {
        // загружаем текстуру один раз при создании типа
        if (!texture.loadFromFile("assets/" + file)) {
            wcerr << L"Ошибка загрузки: " << n << endl;
        }
    }
};

// фабрика, которая управляет пулом наших приспособленцев
// она гарантирует, что мы не будем загружать одну и ту же текстуру дважды
class ObjectFactory {
private:
    // храним созданные типы в мапе, чтобы быстро их находить по названию
    map<wstring, shared_ptr<ObjectType>> types;
public:
    shared_ptr<ObjectType> getType(const wstring& name, const string& file) {
        // если такого типа еще нет - создаем его и сохраняем
        if (types.find(name) == types.end()) {
            types[name] = make_shared<ObjectType>(name, file);
        }
        // возвращаем указатель на уже существующий или только что созданный тип
        return types[name];
    }
};

// контекст или легкий объект на карте
// он хранит только уникальные данные (координаты) и ссылку на тяжелый тип
struct MapObject {
    int x, y;
    shared_ptr<ObjectType> type;

    // отрисовка объекта: берем текстуру из общего типа, но ставим в уникальную позицию
    void draw(sf::RenderWindow& window, int gridSize) {
        sf::Sprite sprite(type->texture);
        sprite.setPosition((float)x * gridSize, (float)y * gridSize);
        // подгоняем размер картинки под размер нашей сетки
        float s = (float)gridSize / type->texture.getSize().x;
        sprite.setScale(s, s);
        window.draw(sprite);
    }
};

// вспомогательный класс для кнопок интерфейса
struct GuiButton {
    sf::RectangleShape shape;
    sf::Text text;
    void init(float x, float y, float w, float h, const wstring& str, sf::Font& font) {
        shape.setPosition(x, y);
        shape.setSize({w, h});
        shape.setFillColor(sf::Color(60, 60, 60));
        shape.setOutlineThickness(1);
        shape.setOutlineColor(sf::Color(150, 150, 150));
        
        text.setFont(font);
        text.setString(str);
        text.setCharacterSize(18);
        text.setPosition(x + 15, y + 12);
    }
    // проверяет, попал ли клик мышки в границы кнопки
    bool isClicked(sf::Vector2f m) { return shape.getGlobalBounds().contains(m); }
};

// состояния приложения и доступные инструменты
enum State { MainMenu, Editor };
enum Tool { Brush, Move, Eraser };

int main() {
    // настраиваем консоль для русского
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);
    setlocale(LC_ALL, "Russian");
    
    sf::RenderWindow window(sf::VideoMode(1200, 800), L"ВАУ-СТРОИТЕЛЬ 3000");
    sf::Font font;
    font.loadFromFile("assets/font.ttf");

    // инициализируем фабрику и список всех объектов на нашей будущей карте
    ObjectFactory factory;
    vector<MapObject> mapObjects;
    State currentState = MainMenu;
    Tool currentTool = Tool::Brush;
    const int GRID_SIZE = 40;

    // формируем каталог всех доступных объектов, разделенный по категориям
    struct Category { wstring label; vector<pair<wstring, string>> items; };
    vector<Category> catalog = {
        { L"ПОВЕРХНОСТЬ", { {L"Река", "river.png"}, {L"Трава", "grass.png"}, {L"Пустыня", "desert.png"}, {L"Дорога", "road.png"}, {L"Мост", "bridge.png"}, {L"Горы", "mountains.png"} } },
        { L"ДЕТАЛИ", { {L"Ель", "spruce.png"}, {L"Дуб", "oak.png"}, {L"Камень", "stone.png"}, {L"Стена", "wall.png"}, {L"Башня", "tower.png"}, {L"Колодец", "well.png"}, {L"Костёр", "fire.png"} } },
        { L"СУЩЕСТВА", { {L"Рыцарь", "knight.png"}, {L"Кабан", "boar.png"}, {L"Орк", "orc.png"} } }
    };


    // начальные настройки: выбранная трава и пустой указатель для переноса объектов
    shared_ptr<ObjectType> selectedType = factory.getType(L"Трава", "grass.png");
    MapObject* movingObject = nullptr;

    // создаем все кнопки интерфейса
    GuiButton btnCreate, btnLoad, btnExit, btnSave, btnBack, btnTBrush, btnTMove, btnTEraser;
    btnCreate.init(475, 300, 250, 50, L"СОЗДАТЬ КАРТУ", font);
    btnLoad.init(475, 370, 250, 50, L"ЗАГРУЗИТЬ КАРТУ", font);
    btnExit.init(475, 440, 250, 50, L"ВЫХОД", font);
    btnTBrush.init(970, 550, 210, 40, L"КИСТЬ", font);
    btnTMove.init(970, 600, 210, 40, L"ПЕРЕМЕСТИТЬ", font);
    btnTEraser.init(970, 650, 210, 40, L"ЛАСТИК", font);
    btnSave.init(970, 710, 210, 40, L"СОХРАНИТЬ", font);
    btnBack.init(970, 755, 210, 35, L"В МЕНЮ", font);

    while (window.isOpen()) {
        sf::Event event;
        // получаем позицию мыши и переводим её в координаты игрового мира
        sf::Vector2f mPos = window.mapPixelToCoords(sf::Mouse::getPosition(window));

        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) window.close();

            if (event.type == sf::Event::MouseButtonPressed && event.mouseButton.button == sf::Mouse::Left) {
                // логика главного меню
                if (currentState == MainMenu) {
                    if (btnCreate.isClicked(mPos)) { currentState = Editor; mapObjects.clear(); }
                    if (btnExit.isClicked(mPos)) window.close();
                    if (btnLoad.isClicked(mPos)) {
                        // блокирующий ввод в консоли для загрузки файла
                        cout << "\n>>> [СИСТЕМА]: ВВЕДИТЕ ИМЯ ФАЙЛА В ТЕРМИНАЛЕ: ";
                        string name; cin >> name;
                        ifstream f("saves/" + name + ".json");
                        if(f) {
                            json j; f >> j; mapObjects.clear();
                            for(auto& o : j["objs"]) {
                                // восстанавливаем объекты, запрашивая их типы у фабрики
                                mapObjects.push_back({o["x"], o["y"], factory.getType(sf::String(o["n"].get<string>()).toWideString(), o["f"])});
                            }
                            currentState = Editor;
                        }
                    }
                } else {
                    // логика редактора
                    if (mPos.x < 950) { // клик по рабочей области карты
                        int gx = (int)mPos.x / GRID_SIZE, gy = (int)mPos.y / GRID_SIZE;
                        if (currentTool == Brush) mapObjects.push_back({gx, gy, selectedType});
                        if (currentTool == Eraser) {
                            // удаляем объект, если его координаты совпадают с кликом
                            mapObjects.erase(remove_if(mapObjects.begin(), mapObjects.end(), [gx, gy](MapObject& o){ return o.x == gx && o.y == gy; }), mapObjects.end());
                        }
                        if (currentTool == Move) {
                            // ищем объект под мышкой, чтобы начать его перемещение
                            for(auto& o : mapObjects) if(o.x == gx && o.y == gy) { movingObject = &o; break; }
                        }
                    } else { // клик по панели управления (справа)
                        if (btnBack.isClicked(mPos)) currentState = MainMenu;
                        if (btnTBrush.isClicked(mPos)) currentTool = Brush;
                        if (btnTMove.isClicked(mPos)) currentTool = Move;
                        if (btnTEraser.isClicked(mPos)) currentTool = Eraser;
                        if (btnSave.isClicked(mPos)) {
                            // сохранение текущей карты в JSON
                            cout << "\n>>> [СИСТЕМА]: ВВЕДИТЕ ИМЯ ДЛЯ СОХРАНЕНИЯ: ";
                            string sname; cin >> sname;
                            json j;
                            for(auto& o : mapObjects) j["objs"].push_back({{"x",o.x},{"y",o.y},{"n",sf::String(o.type->name).toAnsiString()},{"f",o.type->filename}});

                            ofstream f("saves/"+sname+".json"); f << j.dump(4);
                        }
                        // выбор активного типа объекта из списка категорий
                        float currentY = 50;
                        for(auto& cat : catalog) {
                            currentY += 30; // пропускаем заголовок категории
                            for(auto& item : cat.items) {
                                if (sf::FloatRect(970, currentY, 200, 20).contains(mPos)) selectedType = factory.getType(item.first, item.second);
                                currentY += 22;
                            }
                        }
                    }
                }
            }
            // когда отпускаем кнопку мыши, прекращаем перемещение объекта
            if (event.type == sf::Event::MouseButtonReleased) movingObject = nullptr;
        }

        // если мы сейчас что-то перетаскиваем то обновляем координаты объекта вслед за мышью
        if (movingObject) {
            movingObject->x = (int)mPos.x / GRID_SIZE; movingObject->y = (int)mPos.y / GRID_SIZE;
        }

        window.clear(sf::Color(35, 35, 35));

        if (currentState == MainMenu) {
            // отрисовка главного меню
            sf::Text title(L"ВАУ-СТРОИТЕЛЬ КАРТ 3000", font, 55);
            title.setPosition(1200/2.f - title.getGlobalBounds().width/2.f, 120);
            window.draw(title);
            window.draw(btnCreate.shape); window.draw(btnCreate.text);
            window.draw(btnLoad.shape); window.draw(btnLoad.text);
            window.draw(btnExit.shape); window.draw(btnExit.text);
        } else {
            // отрисовка редактора с сетки
            for(int i=0; i<=950; i+=GRID_SIZE) { sf::Vertex l[] = { sf::Vertex({(float)i,0},sf::Color(55,55,55)), sf::Vertex({(float)i,800},sf::Color(55,55,55)) }; window.draw(l, 2, sf::Lines); }
            for(int i=0; i<=800; i+=GRID_SIZE) { sf::Vertex l[] = { sf::Vertex({0,(float)i},sf::Color(55,55,55)), sf::Vertex({950,(float)i},sf::Color(55,55,55)) }; window.draw(l, 2, sf::Lines); }
            
            // рисуем все объекты на карте
            for(auto& o : mapObjects) o.draw(window, GRID_SIZE);
            
            // рисуем правую панель инструментов и список объектов по категориям
            sf::RectangleShape bar({250, 800}); bar.setPosition(950, 0); bar.setFillColor(sf::Color(45, 45, 45)); window.draw(bar);
            float currentY = 50;
            for(auto& cat : catalog) {
                sf::Text head(cat.label, font, 16); head.setFillColor(sf::Color::Cyan); head.setPosition(965, currentY); window.draw(head);
                currentY += 30;
                for(auto& item : cat.items) {
                    sf::Text t(item.first, font, 14); t.setPosition(975, currentY);
                    // подсвечиваем желтым то, что выбрано сейчас
                    if (selectedType->name == item.first) t.setFillColor(sf::Color::Yellow);
                    window.draw(t);
                    currentY += 22;
                }
            }
            // отрисовка кнопок управления редактором
            if (currentTool == Tool::Brush) btnTBrush.shape.setFillColor(sf::Color(100, 100, 30)); 
            else btnTBrush.shape.setFillColor(sf::Color(60, 60, 60)); 
            window.draw(btnTBrush.shape); 
            window.draw(btnTBrush.text);

            if (currentTool == Tool::Move) btnTMove.shape.setFillColor(sf::Color(100, 100, 30));
            else btnTMove.shape.setFillColor(sf::Color(60, 60, 60));
            window.draw(btnTMove.shape); 
            window.draw(btnTMove.text);

            if (currentTool == Tool::Eraser) btnTEraser.shape.setFillColor(sf::Color(100, 30, 30)); 
            else btnTEraser.shape.setFillColor(sf::Color(60, 60, 60));
            window.draw(btnTEraser.shape); 
            window.draw(btnTEraser.text);


            window.draw(btnSave.shape); 
            window.draw(btnSave.text);
            window.draw(btnBack.shape); 
            window.draw(btnBack.text);
        }
        window.display();
    }
    return 0;
}
