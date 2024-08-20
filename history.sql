CREATE TABLE t_paper_index (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    title VARCHAR(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '标题',
    web_url VARCHAR(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '页面链接',
    pdf_url VARCHAR(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'PDF链接',
    authors VARCHAR(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '作者列表',
    reference VARCHAR(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '参考文献',
    md5_hash VARCHAR(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci UNIQUE NOT NULL COMMENT 'MD5(title+authors)',
    dash_scope_req JSON DEFAULT NULL COMMENT '信息抽取的请求参数',
    dash_scope_resp JSON DEFAULT NULL COMMENT '信息抽取的响应结果',
    is_extracted TINYINT DEFAULT 0 COMMENT '是否已抽取',
    is_locked TINYINT DEFAULT 0 COMMENT '是否被锁定(人工修正过,不希望再次被更新)',
    is_deleted TINYINT DEFAULT 0 COMMENT '是否已删除',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间'
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '请求记录表';