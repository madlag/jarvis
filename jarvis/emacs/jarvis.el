;; Initialize Jarvis
(pymacs-load "jarvis.emacs" "j-")
(global-set-key (kbd "C-x g") 'j-goto-error)
(global-set-key (kbd "C-x i") 'j-inspect-vars)
