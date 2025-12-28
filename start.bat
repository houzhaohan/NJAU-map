@echo off
REM 启动app.py并将日志保存到logs文件夹，每次运行生成带时间戳的日志文件

REM 设置日志文件路径和名称，时间戳精确到秒
set "LOG_DIR=logs"
set "TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "LOG_FILE=%LOG_DIR%\app_run_%TIMESTAMP%.log"

REM 检查logs文件夹是否存在，不存在则创建
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 记录启动时间
echo Program startup time: %date% %time% > "%LOG_FILE%"

echo Running app.py
echo To exit, press Control + C

REM 运行app.py并将输出重定向到日志文件
python app.py >> "%LOG_FILE%" 2>&1

REM 检查程序是否正常启动
if %errorlevel% equ 0 (
    echo app.py started successfully! Log file: %LOG_FILE%
) else (
    echo app.py startup failed, please check the log file: %LOG_FILE%
)

REM 记录结束时间
 echo Program end time: %date% %time% >> "%LOG_FILE%"

REM 按任意键退出
pause