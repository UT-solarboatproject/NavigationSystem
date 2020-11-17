# NavigationSystem

This is the algorism that the solar boart can aim the goal automatically
 
# Overview
 
システムの概要
 
# Requirement
 
 
* python 3.8.1
  * formatter: black

 
# Installation
 
mac OSの場合

## pythonのinstall

1. まず pyenv をインストール：

`brew install pyenv`

`pyenv -v`

2. pyenv の設定（.bash_profile の設定変更）：

`echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile`

`echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile`

`echo 'eval "$(pyenv init -)"' >> ~/.bash_profile`

3. Python のアップデート：

3.8.1がダウンロード可能であることを確認
`pyenv install --list`



`pyenv install 3.8.1`

`pyenv versions`

このままだと global（* マーク）が system のままなので, ver.2 系列しか使えない. そこで global を 3.8.1 に変更

`pyenv global 3.8.1`

`pyenv versions`

変更されていることを確認してから, ターミナルを再起動（ここ重要）. 最後にバージョンを確認

`python -V`

これでターミナルから python を実行すれば 3.8.1が使えるようになります.

 
# Usage
 
```bash

```
 
# Note
 
注意点などがあれば書く
 
# Author
 
 
* YukiSaegusa
* University of Tokyo
 
