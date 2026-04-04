#!/usr/bin/env osascript
-- 携程笔记自动填写脚本
-- 使用方法：在 Safari/Chrome 中打开携程发布页面并登录后运行此脚本

on run argv
    set noteTitle to item 1 of argv
    set noteContent to item 2 of argv
    set noteDestination to item 3 of argv
    
    tell application "Google Chrome"
        activate
        
        tell active tab of first window
            -- 等待页面加载
            delay 2
            
            -- 填写标题
            execute javascript "
                (function() {
                    const titleInput = document.querySelector('input[placeholder*=\"标题\"]') || 
                                       document.querySelector('.title-input') ||
                                       document.querySelector('input[maxlength]');
                    if (titleInput) {
                        titleInput.value = '" & noteTitle & "';
                        titleInput.dispatchEvent(new Event('input', { bubbles: true }));
                        return '标题已填写';
                    }
                    return '未找到标题输入框';
                })();
            "
            
            delay 1
            
            -- 填写正文
            execute javascript "
                (function() {
                    const editor = document.querySelector('[contenteditable=\"true\"]') ||
                                   document.querySelector('.editor-content') ||
                                   document.querySelector('textarea');
                    if (editor) {
                        editor.innerHTML = '" & noteContent & "';
                        editor.dispatchEvent(new Event('input', { bubbles: true }));
                        return '正文已填写';
                    }
                    return '未找到编辑器';
                })();
            "
            
            delay 1
            
            -- 填写目的地
            if noteDestination is not "" then
                execute javascript "
                    (function() {
                        const destInput = document.querySelector('input[placeholder*=\"目的地\"]') ||
                                          document.querySelector('.destination-input');
                        if (destInput) {
                            destInput.value = '" & noteDestination & "';
                            destInput.dispatchEvent(new Event('input', { bubbles: true }));
                            return '目的地已填写';
                        }
                        return '未找到目的地输入框';
                    })();
                "
            end if
            
        end tell
    end tell
    
    display notification "携程笔记内容已自动填写，请检查并上传图片后发布" with title "携程发布助手"
end run