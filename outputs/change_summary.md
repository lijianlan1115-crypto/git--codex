# 研发协同变更分析与测试预警报告

> 生成方式：GitHub Actions checkout 目标仓库后，使用硅基流动 OpenAI-compatible API 在 runner 本地读取 diff/context 生成。

模型：Qwen/Qwen2.5-72B-Instruct

# 研发协同影响分析报告

## 1. 变更摘要
本次提交 `a1c3377` 主要支持了业务数据集 v1，并加强了飞书数据信任机制。具体变更包括：
- 增加了对 MySQL 业务数据集 v1 的支持，包括 `room_type_name` 字段的处理。
- 增强了 `frontdesk-tasks` 命令，支持日期参数。
- 修改了 `revenue-decision` 和 `deviation` 命令，增加了历史数据复盘模式。
- 更新了 `market-context` 命令，增加了新的天气 provider 选项。
- 修改了 `tests/test_security_and_freshness.py` 测试用例，增加了对新功能的测试。

## 2. 修改文件清单
- `runtime/adapters/database.py`
- `runtime/cli.py`
- `runtime/decisions/calendar.py`
- `runtime/decisions/command_menu.py`
- `runtime/decisions/deviation.py`
- `runtime/decisions/pricing.py`
- `runtime/decisions/tasks.py`
- `skills/hotel-ota/s03-message-hub/references/rules.md`
- `skills/hotel-ota/s04-market-context/references/rules.md`
- `tests/harness/scenarios/s4_market_mcp.json`
- `tests/test_security_and_freshness.py`

## 3. 影响模块
### 代码模块
- `runtime/adapters/database.py`：增加了对 `room_type_name` 字段的处理，以及对数据库查询结果的诊断。
- `runtime/cli.py`：增加了 `--date` 参数支持。
- `runtime/decisions/calendar.py`：增加了对天气 provider 的规范化处理。
- `runtime/decisions/command_menu.py`：增加了历史数据复盘模式的处理逻辑。
- `runtime/decisions/deviation.py`：增加了历史数据复盘模式的处理逻辑。
- `runtime/decisions/pricing.py`：增加了对历史数据复盘模式的支持。
- `runtime/decisions/tasks.py`：增加了对日期参数的支持。

### 业务模块
- **市场行情感知 (S4)**：增加了新的天气 provider 选项，支持 `wttr_http` 和 `weather_fixture`。
- **智能收益决策 (S5)**：增加了历史数据复盘模式，确保在数据不新鲜时只生成复盘建议。
- **前台任务 (S3/S11)**：增加了对日期参数的支持，确保任务生成时能考虑特定日期的数据。

### Agent
- **总控 Agent (`hotel-ota-chief`)**：需要更新配置以支持新的命令参数和历史数据复盘模式。

### Skill
- **S4 市场行情感知**：需要更新 `references/rules.md` 以支持新的天气 provider 选项。
- **S5 智能收益决策**：需要更新 `references/rules.md` 以支持历史数据复盘模式。
- **S3 前台任务**：需要更新 `references/rules.md` 以支持日期参数。

### 配置
- **环境变量 (`config/env.example`)**：需要确认是否需要新增或修改与新功能相关的环境变量。
- **角色映射 (`config/feishu-role-map.example.json`)**：需要确认是否需要更新角色权限以支持新的命令参数和历史数据复盘模式。

### 输入输出
- **输入**：增加了对日期参数的支持，确保在调用 `frontdesk-tasks` 和 `deviation` 时能传递日期。
- **输出**：增加了对历史数据复盘模式的支持，确保在数据不新鲜时只生成复盘建议。

## 4. 协同风险
- **其他开发**：新功能的引入可能需要其他开发人员更新他们的代码以支持日期参数和历史数据复盘模式。
- **测试环境**：测试环境需要更新以支持新的命令参数和历史数据复盘模式。
- **正式环境**：正式环境需要更新以支持新的命令参数和历史数据复盘模式，确保不会因为数据不新鲜而生成错误的调价建议。
- **其他工作区**：其他工作区如果依赖于这些模块，也需要更新以支持新的功能。

## 5. 风险等级
**中等 (medium)**
- **原因**：虽然本次提交主要是功能增强，但涉及多个模块和命令的修改，需要确保所有相关模块和命令在测试和正式环境中都能正常工作。特别是历史数据复盘模式的引入，需要确保不会影响现有的调价建议生成逻辑。

## 6. 是否需要我同步修改
- **是**：需要同步更新 `config/env.example` 和 `config/feishu-role-map.example.json` 以支持新的命令参数和历史数据复盘模式。
- **否**：不需要修改其他文件，但需要确保所有相关模块和命令在测试和正式环境中都能正常工作。

## 7. 回归验证方案
### 测试什么
- **数据库查询**：验证 `room_type_name` 字段的处理是否正确。
- **命令参数**：验证 `--date` 参数在 `frontdesk-tasks` 和 `deviation` 命令中的传递和处理是否正确。
- **历史数据复盘**：验证在数据不新鲜时，`revenue-decision` 和 `deviation` 命令是否能正确生成复盘建议。
- **天气 provider**：验证新的天气 provider 选项（`wttr_http` 和 `weather_fixture`）是否能正确处理。

### 怎么测
- **数据库查询**：
  ```bash
  .venv/bin/python runtime/hotel_ota_runtime.py database-query --db-kind mysql --template operating_snapshot --hotel-id puyue
  ```
- **命令参数**：
  ```bash
  .venv/bin/python runtime/hotel_ota_runtime.py frontdesk-tasks --hotel-id puyue --date 2026-06-09
  .venv/bin/python runtime/hotel_ota_runtime.py deviation --hotel-id puyue --date 2026-06-09
  ```
- **历史数据复盘**：
  ```bash
  .venv/bin/python runtime/hotel_ota_runtime.py revenue-decision --hotel-id puyue --date 2026-06-09
  .venv/bin/python runtime/hotel_ota_runtime.py deviation --hotel-id puyue --date 2026-06-09
  ```
- **天气 provider**：
  ```bash
  .venv/bin/python runtime/hotel_ota_runtime.py market-context --hotel-id puyue --date 2026-06-09 --weather-provider wttr_http
  .venv/bin/python runtime/hotel_ota_runtime.py market-context --hotel-id puyue --date 2026-06-09 --weather-provider weather_fixture
  ```

## 8. 通过标准
- **数据库查询**：`room_type_name` 字段正确处理，返回结果中包含该字段。
- **命令参数**：`--date` 参数正确传递和处理，生成的任务和偏差诊断结果符合预期。
- **历史数据复盘**：在数据不新鲜时，`revenue-decision` 和 `deviation` 命令生成的复盘建议符合预期。
- **天气 provider**：新的天气 provider 选项（`wttr_http` 和 `weather_fixture`）正确处理，返回结果中包含正确的 `source_quality` 和 `weather_summary`。

## 9. 失败标准
- **数据库查询**：`room_type_name` 字段处理错误，返回结果中缺少该字段。
- **命令参数**：`--date` 参数传递或处理错误，生成的任务和偏差诊断结果不符合预期。
- **历史数据复盘**：在数据不新鲜时，`revenue-decision` 和 `deviation` 命令生成的复盘建议不符合预期。
- **天气 provider**：新的天气 provider 选项（`wttr_http` 和 `weather_fixture`）处理错误，返回结果中 `source_quality` 或 `weather_summary` 不正确。

## 10. 测试清单
- **数据库查询**：
  - `room_type_name` 字段处理
- **命令参数**：
  - `frontdesk-tasks` 命令的 `--date` 参数
  - `deviation` 命令的 `--date` 参数
- **历史数据复盘**：
  - `revenue-decision` 命令的历史数据复盘模式
  - `deviation` 命令的历史数据复盘模式
- **天气 provider**：
  - `market-context` 命令的 `wttr_http` provider
  - `market-context` 命令的 `weather_fixture` provider

## 11. 需要人工确认的点
- **数据库查询**：确认 `room_type_name` 字段的处理是否符合业务需求。
- **命令参数**：确认 `--date` 参数的传递和处理是否符合业务需求。
- **历史数据复盘**：确认在数据不新鲜时，`revenue-decision` 和 `deviation` 命令生成的复盘建议是否合理。
- **天气 provider**：确认新的天气 provider 选项（`wttr_http` 和 `weather_fixture`）是否能正确处理并返回预期结果。

## 12. 报告总结
本次提交主要增强了对业务数据集 v1 的支持，并加强了飞书数据信任机制。涉及多个模块和命令的修改，需要确保所有相关模块和命令在测试和正式环境中都能正常工作。特别是历史数据复盘模式的引入，需要仔细验证其逻辑是否正确，确保不会影响现有的调价建议生成逻辑。建议在测试环境中进行全面测试，确认无误后再部署到正式环境。
