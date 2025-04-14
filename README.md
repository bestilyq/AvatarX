# LatentSync
Custom Latentsync from bytedance/Latentsync

## 使用国内hugging face镜像，设置 HF_ENDPOINT 环境变量
### Linux/Mac OS
```shell
export HF_ENDPOINT="https://hf-mirror.com"
```

### Linux 写入到~/.bashrc中：
```shell
echo 'export HF_ENDPOINT="https://hf-mirror.com"' >> ~/.bashrc
```

### Mac OS 写入到 ~/.zshrc 中：
```shell
echo 'export HF_ENDPOINT="https://hf-mirror.com"' >> ~/.zshrc
```

### Windows Powershell写入到 ~\Documents\WindowsPowerShellMicrosoft.PowerShell_profile.ps1 中：
```powershell
Add-Content -Path $PROFILE -Value '$env:HF_ENDPOINT = "https://hf-mirror.com"'
```

### Python
```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```
>*注意：*os.environ得在import huggingface库相关语句之前执行。

