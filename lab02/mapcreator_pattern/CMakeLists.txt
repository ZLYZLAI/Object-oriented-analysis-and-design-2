cmake_minimum_required(VERSION 3.14)
set(CMAKE_POLICY_DEFAULT_CMP0000 NEW)
set(CMAKE_POLICY_VERSION_MINIMUM 3.5)

project(MapBuilder3000)

set(CMAKE_CXX_STANDARD 17)

# Путь к  распакованной SFML 
set(SFML_DIR "${CMAKE_SOURCE_DIR}/external/SFML-2.6.1/lib/cmake/SFML")
find_package(SFML 2.6 COMPONENTS graphics window system REQUIRED)

# JSON 
include(FetchContent)
FetchContent_Declare(json URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz)
FetchContent_MakeAvailable(json)

add_executable(MapBuilder3000 src/main.cpp)
target_link_libraries(MapBuilder3000 PRIVATE sfml-graphics sfml-window sfml-system nlohmann_json::nlohmann_json)

# Копируем нужные .dll в папку с .exe, чтобы программа запустилась
add_custom_command(TARGET MapBuilder3000 POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    "${CMAKE_SOURCE_DIR}/external/SFML-2.6.1/bin"
    $<TARGET_FILE_DIR:MapBuilder3000>
)
