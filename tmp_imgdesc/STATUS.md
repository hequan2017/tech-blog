# 精读流水线状态(供会话续接,勿提交)

## 任务(用户 2026-09-28 指令)
逐篇: 完整阅读 → 重写内容介绍 → 修复明显错误/笔误 → 排版美化(分节+代码块+注释)
含图文章: 看图写中文 alt 描述(8~30字)
每篇单独提交(msg: docs: 精读《标题》摘要)并 push
全部完成后: 整理目录,把根目录散落的 *.py 移入一个目录(scripts/ 已存在,内有旧脚本)

## 状态
- 之前另一会话已完成精读 15 篇(见 done_files.txt,git log 精读 提交)
- queue.json: 剩余待处理(401 篇,按时间排序),wave 从头取
- wave N 生成: `python -c` 从 queue.json 取 (N-1)*24 .. N*24 分 3 份写到 waves/wN_a{1,2,3}.txt
- 代理完成后: `python scripts_wave_commit.py tmp_imgdesc/waves/wN_a*_result.txt` 逐篇提交+push
- 提交后把该批文件名追加进 done_files.txt

## 协作规程(重要)
存在另一个并发流也在逐篇精读并提交(不按时间序)。因此:
1. 每次开新 wave 前,先 `git fetch` + `git log origin/main --grep='docs: 精读《' --name-only --format=` 重建 done 集合(归一化去掉 posts/ 前缀)
2. done_files.txt 统一存**裸文件名**(无 posts/ 前缀)
3. wave 分配排除 done + 在途 wave 文件
4. 提交脚本已加 pull --rebase 与 Co-Authored-By
5. 代理提示词中已有:若文章已被处理过,保留已有良好内容,只查漏补缺

## 已完成 wave
- wave1/2/3/4 (各 24 篇): ✅ 已提交推送
- wave5 (24 篇): 运行中
- 2026-09-28 21:05 状态: done=243/416, 剩余≈150(并发流也在做)
- 每波前: git fetch + git log 精读 grep 重建 done;排除 git status 里并发流 WIP 文件
