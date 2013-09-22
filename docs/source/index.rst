Welcome to Jarvis's documentation!
==================================

.. _OpenSceneGraph: http://www.openscenegraph.org
.. _`Jarvis Front Page`: http://madlag.github.com/jarvis/
.. _`Bret Victor`: http://worrydream.com/ 
.. _`Inventing on Principle`: http://www.youtube.com/watch?v=PUv66718DII
.. _`Light Table`: http://www.kickstarter.com/projects/ibdknox/light-table

Jarvis is a Python coding companion. Point it to a python function, and it will execute it. As soon as you change and save your code, Jarvis will detect it, and will rerun the function.

If an exception is raised, it will be displayed in the error panel.

If you insert some debugging statements in your code, they will be displayed in the debug panel.

Last, but not least, if you are using OpenSceneGraph_ Python bindings, you will be able to output an OSG tree to the Jarvis interface. This way, you can instantly see the new 3D scene your code is generating.

Demo Video
==========

You can have a better description and a *demo video* on the `Jarvis Front Page`_.

Inspiration
===========

Jarvis was inspired by works of `Bret Victor`_, especially his talk `Inventing on Principle`_ .

The central idea is that the feedback loop when you are coding should be the shortest possible, so you can see the effect of your code changes instantly, or almost.
Jarvis implements a (small) subset of these ideas.

Those ideas are also used in the `Light Table`_ KickStarter project.

Installing
==========
1. ``pip install jarvis``
1b. install pymacs and jinja2 if you want to use emacs bindings
2. ``jarvis_server``
3. open http://127.0.0.1:9017/static/index.html in your browser or run ``j_open_jarvis_window``
4. ``jarvis_agent_pythonrunner``
5. ``j-test-this`` on opened python file
``from jarvis.commands import debug

def main():
    debug("Hello world"")```



Full Content
============
.. toctree::
   :maxdepth: 3

   commands
   emacs  

