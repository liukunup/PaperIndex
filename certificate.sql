CREATE TABLE t_certificate (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    platform VARCHAR(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL comment '平台',
    model VARCHAR(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL comment '模型',
    data JSON NOT NULL COMMENT '请求鉴权凭证',
    unused_token_num BIGINT DEFAULT 0 COMMENT 'Token剩余量',
    owner VARCHAR(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL comment '所有者',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间'
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '鉴权凭证表';
