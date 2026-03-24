#include <SFML/Graphics.hpp>
#include <nlohmann/json.hpp>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <windows.h> 
#include <filesystem>
// Мы удалили <map> и <memory>, так как больше не используем умные указатели и кэширование

using namespace std;
using json = nlohmann::json;

// Теперь у нас нет разделения на "Тяжелый тип" и "Легкий контекст на карте".
// У нас есть один "Толстый" объект, который хранит в себе АБСОЛЮТНО ВСЁ.
struct MapObject {
    int x, y;
    wstring name;
    string filename;
    
    // ПРОВАЛ В ПАМЯТИ #1:
    // Текстура (самая тяжелая часть) теперь лежит внутри КАЖДОГО блока на карте.
    // 1000 блоков травы = 1000 одинаковых текстур в оперативной памяти и видеопамяти.
    sf::Texture texture;

    MapObject(int startX, int startY, const wstring& n, const string& file) {
        x = startX;
        y = startY;
        name = n;
        filename = file;
        
        // ПРОВАЛ В ПРОИЗВОДИТЕЛЬНОСТИ #2:
        // Мы обращаемся к жесткому диску (очень медленная операция) 
        // КАЖДЫЙ РАЗ, когда кисть ставит новый блок на карту.
        if (!texture.loadFromFile("assets/" + filename)) {
            wcerr << L"Ошибка загрузки: " << name << endl;
        }
    }

    // Отрисовка работает так же, но теперь мы берем текстуру "из себя", а не из общего типа
    void draw(sf::RenderWindow& window, int gridSize) {
        sf::Sprite sprite(texture);
        sprite.setPosition((float)x * gridSize, (float)y * gridSize);
        float s = (float)gridSize / texture.getSize().x;
        sprite.setScale(s, s);
        window.draw(sprite);
    }
};

// Вспомогательный класс для кнопок интерфейса остался без изменений
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
    bool isClicked(sf::Vector2f m) { return shape.getGlobalBounds().contains(m); }
};

enum State { MainMenu, Editor };
enum Tool { Brush, Move, Eraser };

int main() {
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);
    setlocale(LC_ALL, "Russian");
    
    sf::RenderWindow window(sf::VideoMode(1200, 800), L"ВАУ-СТРОИТЕЛЬ 3000 (ТОРМОЗ-ЭДИШН)");
    sf::Font font;
    font.loadFromFile("assets/font.ttf");

    // Фабрики больше нет. Есть только массив тяжелых объектов.
    vector<MapObject> mapObjects;
    State currentState = MainMenu;
    Tool currentTool = Tool::Brush;
    const int GRID_SIZE = 40;

    struct Category { wstring label; vector<pair<wstring, string>> items; };
    vector<Category> catalog = {
        { L"ПОВЕРХНОСТЬ", { {L"Река", "river.png"}, {L"Трава", "grass.png"}, {L"Пустыня", "desert.png"}, {L"Дорога", "road.png"}, {L"Мост", "bridge.png"}, {L"Горы", "mountains.png"} } },
        { L"ДЕТАЛИ", { {L"Ель", "spruce.png"}, {L"Дуб", "oak.png"}, {L"Камень", "stone.png"}, {L"Стена", "wall.png"}, {L"Башня", "tower.png"}, {L"Колодец", "well.png"}, {L"Костёр", "fire.png"} } },
        { L"СУЩЕСТВА", { {L"Рыцарь", "knight.png"}, {L"Кабан", "boar.png"}, {L"Орк", "orc.png"} } }
    };

    // Вместо указателя на общий тип, мы просто храним строки того, что выбрали в меню
    wstring selectedName = L"Трава";
    string selectedFilename = "grass.png";
    MapObject* movingObject = nullptr;

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
        sf::Vector2f mPos = window.mapPixelToCoords(sf::Mouse::getPosition(window));

        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) window.close();

            if (event.type == sf::Event::MouseButtonPressed && event.mouseButton.button == sf::Mouse::Left) {
                if (currentState == MainMenu) {
                    if (btnCreate.isClicked(mPos)) { currentState = Editor; mapObjects.clear(); }
                    if (btnExit.isClicked(mPos)) window.close();
                    if (btnLoad.isClicked(mPos)) {
                        cout << "\n>>> [СИСТЕМА]: ВВЕДИТЕ ИМЯ ФАЙЛА В ТЕРМИНАЛЕ: ";
                        string name; cin >> name;
                        ifstream f("saves/" + name + ".json");
                        if(f) {
                            json j; f >> j; mapObjects.clear();
                            for(auto& o : j["objs"]) {
                                // ПРОВАЛ #3: При загрузке карты из 1000 объектов, мы 1000 раз 
                                // заставим жесткий диск читать файлы изображений
                                mapObjects.push_back(MapObject(
                                    o["x"], 
                                    o["y"], 
                                    sf::String(o["n"].get<string>()).toWideString(), 
                                    o["f"]
                                ));
                            }
                            currentState = Editor;
                        }
                    }
                } else {
                    if (mPos.x < 950) { 
                        int gx = (int)mPos.x / GRID_SIZE, gy = (int)mPos.y / GRID_SIZE;
                        if (currentTool == Brush) {
                            // Создаем новый уникальный блок. При каждом клике читается картинка с диска!
                            mapObjects.push_back(MapObject(gx, gy, selectedName, selectedFilename));
                        }
                        if (currentTool == Eraser) {
                            mapObjects.erase(remove_if(mapObjects.begin(), mapObjects.end(), [gx, gy](MapObject& o){ return o.x == gx && o.y == gy; }), mapObjects.end());
                        }
                        if (currentTool == Move) {
                            for(auto& o : mapObjects) if(o.x == gx && o.y == gy) { movingObject = &o; break; }
                        }
                    } else { 
                        if (btnBack.isClicked(mPos)) currentState = MainMenu;
                        if (btnTBrush.isClicked(mPos)) currentTool = Brush;
                        if (btnTMove.isClicked(mPos)) currentTool = Move;
                        if (btnTEraser.isClicked(mPos)) currentTool = Eraser;
                        if (btnSave.isClicked(mPos)) {
                            cout << "\n>>> [СИСТЕМА]: ВВЕДИТЕ ИМЯ ДЛЯ СОХРАНЕНИЯ: ";
                            string sname; cin >> sname;
                            json j;
                            // Сохранение почти не изменилось, просто берем данные напрямую из объекта
                            for(auto& o : mapObjects) j["objs"].push_back({{"x",o.x},{"y",o.y},{"n",sf::String(o.name).toAnsiString()},{"f",o.filename}});
                            ofstream f("saves/"+sname+".json"); f << j.dump(4);
                        }
                        
                        float currentY = 50;
                        for(auto& cat : catalog) {
                            currentY += 30; 
                            for(auto& item : cat.items) {
                                if (sf::FloatRect(970, currentY, 200, 20).contains(mPos)) {
                                    // Запоминаем только строки
                                    selectedName = item.first;
                                    selectedFilename = item.second;
                                }
                                currentY += 22;
                            }
                        }
                    }
                }
            }
            if (event.type == sf::Event::MouseButtonReleased) movingObject = nullptr;
        }

        if (movingObject) {
            movingObject->x = (int)mPos.x / GRID_SIZE; movingObject->y = (int)mPos.y / GRID_SIZE;
        }

        window.clear(sf::Color(35, 35, 35));

        if (currentState == MainMenu) {
            sf::Text title(L"ВАУ-СТРОИТЕЛЬ КАРТ 3000", font, 55);
            title.setPosition(1200/2.f - title.getGlobalBounds().width/2.f, 120);
            window.draw(title);
            window.draw(btnCreate.shape); window.draw(btnCreate.text);
            window.draw(btnLoad.shape); window.draw(btnLoad.text);
            window.draw(btnExit.shape); window.draw(btnExit.text);
        } else {
            for(int i=0; i<=950; i+=GRID_SIZE) { sf::Vertex l[] = { sf::Vertex({(float)i,0},sf::Color(55,55,55)), sf::Vertex({(float)i,800},sf::Color(55,55,55)) }; window.draw(l, 2, sf::Lines); }
            for(int i=0; i<=800; i+=GRID_SIZE) { sf::Vertex l[] = { sf::Vertex({0,(float)i},sf::Color(55,55,55)), sf::Vertex({950,(float)i},sf::Color(55,55,55)) }; window.draw(l, 2, sf::Lines); }
            
            for(auto& o : mapObjects) o.draw(window, GRID_SIZE);
            
            sf::RectangleShape bar({250, 800}); bar.setPosition(950, 0); bar.setFillColor(sf::Color(45, 45, 45)); window.draw(bar);
            float currentY = 50;
            for(auto& cat : catalog) {
                sf::Text head(cat.label, font, 16); head.setFillColor(sf::Color::Cyan); head.setPosition(965, currentY); window.draw(head);
                currentY += 30;
                for(auto& item : cat.items) {
                    sf::Text t(item.first, font, 14); t.setPosition(975, currentY);
                    // Подсветка выбранного инструмента сверяется по строке
                    if (selectedName == item.first) t.setFillColor(sf::Color::Yellow);
                    window.draw(t);
                    currentY += 22;
                }
            }

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