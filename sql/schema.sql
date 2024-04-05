-- Создание таблицы баннеров
CREATE TABLE banners
(
    id         SERIAL PRIMARY KEY,
    feature_id INTEGER NOT NULL,
    content    JSONB   NOT NULL,
    is_active  BOOLEAN   DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы тегов
CREATE TABLE tags
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Создание таблицы фич
CREATE TABLE features
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Создание таблицы связей баннеров и тегов
CREATE TABLE banner_tags
(
    banner_id INTEGER REFERENCES banners (id),
    tag_id    INTEGER REFERENCES tags (id),
    PRIMARY KEY (banner_id, tag_id)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    token VARCHAR(100) UNIQUE
);

CREATE INDEX idx_banners_feature_id ON banners (feature_id);

CREATE INDEX idx_banner_tags_tag_id ON banner_tags (tag_id);

CREATE INDEX idx_features_id ON features (id);

CREATE INDEX idx_tags_id ON tags (id);
