/**
 *
 */

if(typeof(toolkit) == "undefiend" || typeof(toolkit.widget) == "undefined") {
    console.error("O 'toolkit.widget' não está presente.");
}

/**
 * Trabalho para migração para ExtJS 4.x
 **/
Ext.apply(Ext, {

    '_create': function(className, cfg) {
        var Class = eval(className);
        try {
            return new Class(cfg);
        }
        catch(e) {
            console.error('Não pude encontrar a definição da classe %s', className);
            throw e;
        }
    },

    '_define': function(className, cfg) {
        var singleton, statics;
        var extend = Object;
        var Klass;
        var mixinsExtend = {};
        var mixinClass;
        var attr;
        var xtype = core.nullValue(cfg.xtype, false);

        Ext.ns(className);

        if(cfg.extend) {
            extend = eval(cfg.extend);
            if(extend == 'undefined')
                console.error('class '+ cfg.extend +' not loaded at this point!');
            delete cfg.extend;
        }

        if(cfg.singleton) {
            singleton = cfg.singleton;
            delete cfg.singleton;
        }

        if(cfg.statics) {
            statics = cfg.statics;
            delete cfg.statics;
        }

        eval(className + ' = Ext.extend(extend, cfg)');
        Klass = eval(className);

        if(Klass.prototype.mixins instanceof Array)
            for(attr in Klass.prototype.mixins) {
                try {
                    mixinClass = eval(attr);
                    Ext.applyIf(mixinsExtend, mixinClass.prototype);
                }
                catch(e) {}
            }
        else
            for(attr in Klass.prototype.mixins) {
                try {
                    mixinClass = eval(Klass.prototype.mixins[attr]);
                    Ext.applyIf(mixinsExtend, mixinClass.prototype);
                }
                catch(e) {}
            }

        // if(mixinsExtend['constructor'])
        //     delete mixinsExtend['constructor'];
        // for(attr in mixinsExtend) {
        //     console.debug(attr);
        // }

        Ext.applyIf(Klass.prototype, mixinsExtend);

        if(singleton)
            Ext.apply(Klass, singleton);

        if(statics)
            Ext.apply(Klass, statics);

        if(xtype != false)
            Ext.reg(xtype, Klass);

        return eval(className);
    }
});

Ext.def = Ext._define;


/**
 * Application
 */
toolkit.Application = {

    msgCt: null,

    viewport: null,

    tabspace: null,

    containers : {
        functions : null
    },

    tree: null,

    panels : {
        left: null,
        right: null,
        center: null
    },

    _tabCount: 0,

    /**
     * Cria um form para manipular um controller, é utilizado principalmente no menu.
     * @param controller, String com o nome do controller.
     */
    createFormFor: function(controller, openNewTab=false) {
        var mask = new Ext.LoadMask(Ext.getBody(), {
            'msg': 'Carregando funcionalidade...'
        });

        mask.show();
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(controller, "json", [controller,]),
            method: 'GET',
            callback: function()
            {
                try
                {
                    if(toolkit.Application.windowMenu.isVisible())
                        Ext.getCmp('btn-athenas-menu').toggle();
                }
                catch(e) {}
                mask.hide();
            },
            success: function(request)
            {
                try
                {

                    if (openNewTab) {
                        var newtab = new Ext.Panel({
                            closable: true,
                            title: 'Carregando...',
                            listeners: {
                                render: function(){
                                    setTimeout(function(){
                                        Ext.decode(request.responseText).show();
                                        setTimeout(function () { toolkit.Application.tabspace.ownerCt.doLayout(); }, 1);
                                    }, 1);
                                }
                            }
                        });

                        toolkit.Application.tabspace.add(newtab);
                        toolkit.Application.tabspace.setActiveTab(newtab);

                    } else {
                        Ext.decode(request.responseText).show();
                        setTimeout(function () { toolkit.Application.tabspace.ownerCt.doLayout(); }, 1);

                    }

                }
                catch(e)
                {
                    Ext.Msg.show({
                        'title': 'Athenas',
                        'icon': Ext.Msg.ERROR,
                        'buttons': Ext.Msg.OK,
                        'msg': 'Não foi possivel atender a sua solicitação.\n' +
                                'A funcionalidade não esta instalado ou apresentou algum defeito.\n' +
                                'Informe ao suporte do Athenas para que o problema possa ser solucionado.'
                    });
                    // console.log(e.message);
                    console.warn(
                        "Ocorreu um erro criando a janela para o controller %s. Comunique a equipe de desenvolvimento.\n%s",
                        controller, e.message
                    );
                }
            },
            failure: function(request)
            {
                Ext.Msg.show({
                    'title': 'Athenas',
                    'icon': Ext.Msg.ERROR,
                    'buttons': Ext.Msg.OK,
                    'msg': "Ocorreu um erro criando a janela para o controller " + controller + ". Comunique a equipe de desenvolvimento."
                });
            }
        });
    },

    /**
     * Metodo utilizado para criar o menu do Workspace.
     * @return Retorna uma arvore como menu.
     * TODO: Implementar o menu da forma como foi planejado.
     */
    createMenu: function(panel) {
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action("Application", "get_menu"),
            params: {
                node: 0
            },
            success: function(request) {
                var result = Ext.decode(request.responseText);
                this.removeAll();

                Ext.each(
                    result,
                    function(record) {
                        var np = new Ext.Panel({
                            title: record.text,
                            iconCls: record.cls.substring('tree-'.length),
                            autoScroll: true,
                            cls: 'larger-font',
                            border: false,
                            collapsed: record.id == 136?false:true,
                            bodyStyle: 'border-bottom:1px solid #99BBE8',
                            items: [
                                new Ext.tree.TreePanel({
                                    layout: "fit",
                                    border: false,

                                    useArrows: false,
                                    autoScroll: true,
                                    containerScroll: true,
                                    animate: true,
                                    //cls: 'button-highlight',
                                    loader: new Ext.tree.TreeLoader({
                                        dataUrl: toolkit.util.Normalize.controller_action("Application", "get_menu"),
                                        preloadChildren: true
                                    }),
                                    rootVisible: false,
                                    root: {
                                        nodeType: 'async',
                                        text: 'Aplicativos',
                                        draggable: false,
                                        id: record.id
                                    },
                                    listeners: {
                                        render: function() {
                                            if(this.loadPanel == undefined) {
                                                this.loadPanel = new Ext.Template(
                                                    '<div class="x-tree-loader">',
                                                        '<p>Carregando...</p>',
                                                    '</div>'
                                                ).insertAfter(
                                                    this.getEl(),
                                                    {},
                                                    true
                                                );
                                            }
                                        },
                                        load: function() {
                                            if(this.loadPanel) {
                                                this.loadPanel.dom.parentNode.removeChild(this.loadPanel.dom);
                                                this.loadPanel = false;
                                            }
                                        }
                                    }
                                })
                            ]
                        });

                        this.add(np);
                    },
                    panel
                );

                // this.add(acc);
                this.doLayout();
            },
            scope: panel
        });
    },

    /**
     * Alert modificado utilizando Ext.MessageBox
     * @param message, Messagem a ser mostrada ao usuário.
     */
    alert: function(message) {
        Ext.MessageBox.show({
            title: "ManagerNetWork",
            msg: message,
            buttons: Ext.MessageBox.OK,
            icon: Ext.MessageBox.WARNING,
            minWidth: 300
        });
    },

    createFormLogin: function() {
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
                'ExtLogin',
                'json'
            ),
            method: 'POST',
            success: function(request) {
                var form = Ext.decode(request.responseText);
                form.show();
            },
            failure: function(request) {
                console.debug(request);
            },
            waitMsg: 'Verificando sua sessão.'
        });

        if (DEBUG) {
            core.DebugInformation.start()
        };
    },

    // _TODEL_ Existe uma nova implementação para "Informações do usuário" no novo Dashboard.
    // getUserInformation: function() {
    //     if (!toolkit.Application._userInformation) {
    //         toolkit.Application._userInformation = new Ext.Window({
    //             border: false,
    //             closable: false,
    //             draggable: false,
    //             resizable: false,
    //             width: 300,
    //             items: Ext._create('toolkit.iget.UserInformation', {
    //                 title: 'Informações do usuário',
    //             }),
    //         });
    //     }

    //     return toolkit.Application._userInformation;
    // },

    getTasksOnDemandMenu: function (sessionInformation) {
        if (toolkit.Application._tasksOnDemandMenu) {
            return toolkit.Application._tasksOnDemandMenu;
        }

        var className = 'core.dashboard.tasksondemand.DropdownMenu';
        toolkit.Application._tasksOnDemandMenu = Ext._create(className, {
            hidden:sessionInformation.access_reports?false:true,
            text: 'Relatórios',
            icon: ['/', global.Context, '/static/images/printer-color.png'].join(''),
        });

        return toolkit.Application._tasksOnDemandMenu;
    },

    getUserInformationWindow: function () {
        if (toolkit.Application._userInfoWindow) {
            return toolkit.Application._userInfoWindow;
        }

        toolkit.Application._userInfoWindow = Ext._create('Ext.Window', {
            border: false,
            closable: false,
            draggable: false,
            resizable: false,
            width: 284,
            items: Ext._create('core.dashboard.userinfo.UserInformationPanel', {
                title: 'Informações do usuário',
            }),
        });

        return toolkit.Application._userInfoWindow;
    },

    getUserInformationButton: function () {
        if (toolkit.Application._userInformationButton) {
            return toolkit.Application._userInformationButton;
        }

        toolkit.Application._userInformationButton = Ext._create('Ext.Button', {
            enableToggle: true,
            text: 'Informações do usuário',
            xKey: 'user-info',  // O nome do usuário é setado no botão
            icon: '/' + global.Context + '/static/images/athenas-user-info.png',
            //toggleGroup: 'btnsInfoUser',
            toggleHandler: function(button, pressed) {
                var userInfoWindow = toolkit.Application.getUserInformationWindow();

                if (pressed) {
                    userInfoWindow.show();
                    userInfoWindow.alignTo(button.getEl(), 'tr-br');
                } else {
                    userInfoWindow.hide();
                }
            },
        });

        return toolkit.Application._userInformationButton;
    },

    changePassword: function() {
        Ext._create('Ext.Window', {
            title: 'Recuperação de Senha',
            modal: true,
            frame: true,
            layout: 'fit',
            autoHeight: true,
            autoWidth: true,
            items: [
                Ext._create('toolkit.iget.ChangePasswordForm'),
            ],
            listeners: {
                close: function(window) {
                    window.destroy();
                }
            }
        }).show();
    },

    // _TODEL_ createIntranet
    // createIntranet: function() {
    //     var thereIs = Ext.getCmp('intranet-app');

    //     if (!thereIs) {
    //         toolkit.Application.createFormFor('Intranet');
    //     }
    // },

    createDashboard: function() {
        var dashboardExists = Ext.getCmp('cmp-dashboard-app');
        if (!dashboardExists) {
            toolkit.Application.createFormFor('Dashboard');
        }
    },

    executeHashURL: function(){
        var hashURL = location.hash.substring(2).split('/');
        var action = hashURL[0]
        var uuid = hashURL[1]

        if (action == 'open'){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action("Application", "get_leaf_controller"),
                params: {
                    action: action,
                    uuid: uuid
                },
                method: 'POST',
                scope: this,
                success: function (request) {
                    var result = Ext.decode(request.responseText);
                    if (result.success) {
                        var controller = result.controller;
                        toolkit.Application.createFormFor(controller, true);
                    }
                    else {
                        Ext.Msg.show({
                            title: 'Athenas',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: result.message
                        });
                    }
                },
                failure: function(){
                    Ext.Msg.show({
                        'title': 'Athenas',
                        'icon': Ext.Msg.ERROR,
                        'buttons': Ext.Msg.OK,
                        'msg': 'Não foi possivel atender a sua solicitação.\n' +
                            'A funcionalidade não esta instalado ou apresentou algum defeito.\n' +
                            'Informe ao suporte do Athenas para que o problema possa ser solucionado.'
                    });
                },
                callback: function(){
                    if ("pushState" in history)
                        history.pushState("", document.title, location.pathname)
                }
            });
        }
    },

    createWorkspace: function(sessionInformation) {
        toolkit.Application.tabspace = new Ext.TabPanel({
            activeTab: 0,
            border: false,
            listeners: {
                afterlayout: function(panel) {
                    panel.items.each(
                        function(panel) {
                            panel.doLayout();
                        }
                    )
                },
                afterrender: function(cmp){
                    //console.debug(toolkit.util.Notification.updateNotification);
                    toolkit.util.Notification.startTaskToolTip();
                    toolkit.util.Tasks.startTaskToolTip();
                    // Ext.select('#top-toolbox .change-password').on('click', toolkit.Application.changePassword);
                    Ext.select('#top-toolbox .end-session').on('click', toolkit.Application.endSession);
                },
            },
            resizeTabs: true,
            minTabWidth: 115,
            tabWidth:195,
            enableTabScroll:true
        });

        toolkit.Application.viewport = new Ext.Viewport({
            layout: 'border',
            border: false,
            listeners: {
                afterrender: function(view) {
                    toolkit.Application.windowMenu = Ext._create('core.GlobalMenu', {
                        width: 300,
                        frame: true,
                        draggable: false,
                        resizable: false,
                        height: (Ext.getBody().getBox().height * 0.8),
                        //targetEl: toolkit.Application.getAthenasButtonMenu().getEl(),
                        layout: 'vbox',
                        layoutConfig: {align: 'stretch'},
                        items: [
                            {
                                border: false,
                                layout: 'accordion',
                                flex: 1,
                                listeners: {
                                    render: function(panel) {
                                        toolkit.Application.createMenu(panel);
                                    }
                                }
                            }
                        ]
                    });
                }
            },
            items: toolkit.Application.factoryItemsViewport(sessionInformation)
        });

        toolkit.Application.viewport.render();

        // _TODEL_ Existe uma nova implementação para "Informações do usuário" no novo Dashboard.
        Ext.Ajax.request({
            url: toolkit.util.action('UserInformation/refresh'),
            success: function(response)
            {
                var obj = Ext.decode(response.responseText);
                if(obj)
                {
                    var bbar = toolkit.Application.viewport.items.get(0).getBottomToolbar();
                    var btn = bbar.find('xKey', 'user-info').shift();

                    // _TODO_ Transferir implementação para o Dashboard
                    btn.setText(obj.nome);

                    if(localStorage)
                        localStorage.setItem('user-info', JSON.stringify(obj));
                }
            }
        })

        var notifyManage = Ext._create('engine.notify.Manage');
        notifyManage.render();

        core.RemoteObserver.init();

        core.RemoteObserver.on('report-ready', {
            scope: this,
            fn: function (data) {
                console.info('report-ready', data);
                toolkit.util.downloadFile({
                    url: data.path,
                    filename: data.filename,
                    approach: 'download',
                });
            },
        });

        var sentinel = Ext.TaskMgr.start({
            interval: (30 * 1000),
            run: function() {
                Ext.Ajax.request({
                    url: core.callAction('Application', 'get_session_information'),
                    method: 'GET',
                    success: function(request) {
                        var result = Ext.decode(request.responseText);
                        sentinel.errCount = 0;

                        if(!result.is_auth)
                            location.reload(true);

                        notifyManage.observe(result.notifications);

                        // Atualiza texto do botão/menu "Relatórios" (Tarefas sob demanda)
                        var tasksOnDemandMenu = Ext.getCmp('cmp-tasks-on-demand-menu');
                        if (tasksOnDemandMenu && result.notifications.hasOwnProperty('tasker')) {
                            tasksOnDemandMenu.updateCount(result.notifications.tasker);
                        }
                    },
                    failure: function() {
                        sentinel.errCount = (sentinel.errCount || 0) + 1;

                        console.log('Sentinel error count %d de %d', sentinel.errCount, 3);

                        if(sentinel.errCount > 3)
                            Ext.Msg.show({
                                title: 'Manutenção',
                                msg: 'O sistema esta passando por alguma dificuldade, caso esteja editando algum ' +
                                     'documento copie-o em outro editor para não perde-lo. ' +
                                     'Deseja finalizar a sessão?',
                                icon: Ext.Msg.QUESTION,
                                buttons: Ext.Msg.YESNO,
                                fn: function(btn) {
                                    sentinel.errCount = 0;
                                    if(btn == 'yes')
                                        location.reload();
                                }
                            });
                    }
                });
            }
        });

        // _TODO_ Aqui fica a primeira chamada de criação do Dashboard
        //var defaultPanel = (localStorage.getItem('defaultPanel') || 'Intranet');
        var defaultPanel = (localStorage.getItem('defaultPanel') || 'Dashboard');
        toolkit.Application.createFormFor(defaultPanel);
        toolkit.Application.executeHashURL();
        toolkit.Application.startEventos();

        core.DebugInformation.start();
        // stats.Colector.send();
    },

    getMenuPanel: function () {
        if (this._menuPanel) {
            return this._menuPanel;
        }

        this._menuPanel = Ext._create('Ext.Panel', {
            layout: 'accordion',
            region: 'west',
            title: 'Menu de Aplicativos',
            width: 300,
            minWidth: 250,
            split: true,
            collapsible: true,
            bodyStyle: 'background-color: #005a7d',
            listeners: {
                render: function(panel) {
                    toolkit.Application.createMenu(panel);
                },
                hide: function (panel) {
                    toolkit.Application.viewport.doLayout();
                },
                show: function (panel) {
                    toolkit.Application.viewport.doLayout();
                },
            },
        });

        return this._menuPanel;
    },

    factoryItemsViewport: function(sessionInformation) {
        var tpl = new Ext.Template(
            '<div id="header">',
                '<h1>Portal do Servidor</h1>',
                '<div id="top-toolbox">',
                    // '<button class="change-password rounded">Alterar Senha</button>',
                    // '<span class="separator">|</span>',
                    '<button class="end-session rounded">Finalizar Sessão</button>',
                '</div>',
            '</div>'
        );

        var items = [
            {
                region: 'north',
                layout: 'fit',
                style: {
                    height: 56
                },
                html: tpl.apply(),
                bbar: [
                    {
                        iconCls: true,
                        icon: '/' + global.Context + '/static/images/tab_new.png',
                        handler: function() {
                            var ntitle = "Nova aba " + (++toolkit.Application._tabCount);
                            var newtab = new Ext.Panel({
                                title: ntitle,
                                tooltip: ntitle,
                                closable: true
                            });

                            toolkit.Application.tabspace.add(newtab);
                            toolkit.Application.tabspace.setActiveTab(newtab);
                        },
                        scope: this,
                        tooltip: "Cria uma nova aba na área de trabalho."
                    },
                    '-',
                    {
                        text: 'Inicial',
                        icon: '/' + global.Context + '/static/images/home.png',
                        cls: 'button-highlight',
                        //handler: this.createIntranet
                        handler: this.createDashboard,
                    },
                    '-',
                    {
                        text: 'Ajuda',
                        icon: '/' + global.Context + '/static/images/question.png',
                        cls: 'button-highlight',
                        handler: function(){
                            window.open("https://mp-mt.atlassian.net/wiki/spaces/MAN/pages/6100841/Athenas+Suite");
                        },
                    },
                    // '-',
                    // {
                    //     text: 'Portal Conecta MPTO',
                    //     icon: '/' + global.Context + '/static/images/applications-internet.png',
                    //     cls: 'button-highlight',
                    //     handler: function(){
                    //         window.location.href = "https://intranet.mpto.mp.br";
                    //     },
                    // },
                    '-',
                    toolkit.Application.getTasksOnDemandMenu(sessionInformation),

                    // _TODEL_ Em razão do novo Dashboard, funcionalidade "Manuais" transferida
                    {
                        hidden: true,
                        // id: 'btn-athenas-manuals',
                        xtype: 'button',
                        text: 'Manuais',
                        icon: '/' + global.Context + '/static/images/application-pdf.png',
                        cls: 'button-highlight',
                        handler: function(btn) {
                            if (toolkit.web.intranet.News) {
                                var news = new toolkit.web.intranet.News();
                                new Ext.Window({
                                    // id: 'intranet-manuals-modal',
                                    title: 'Manuais',
                                    modal: true,
                                    autoScroll: true,
                                    height: 500,
                                    width: 450,
                                    items: [news],
                                    bbar: [news.getPaging()],
                                    listeners: {
                                        afterrender: function(cmpWindow)
                                        {
                                            news.getStoreAreas(function(storeAreas) {
                                                var store = news.getStore();
                                                store.setBaseParam('areas__slug__in', '[\'manuais\']');
                                            });
                                        }
                                    }
                                }).show();
                            } else {
                                Ext.Msg.alert('Erro!', 'Aplicativo toolkit.web.intranet não instalado.');
                            }
                        }
                    },

                    // _TODEL_ Em razão do novo Dashboard, funcionalidade "Menu Athenas" transferida
                    {
                        hidden: true,
                        id: 'btn-athenas-menu',
                        xtype: 'button',
                        text: 'Athenas',
                        enableToggle: true,
                        cls: 'button-highlight',
                        icon: '/' + global.Context + '/static/images/athenas-menu-3.png',
                        toggleHandler: function(btn, st)
                        {
                            toolkit.Application.windowMenu.toogleMenu();
                            if(st)
                                toolkit.Application.windowMenu.alignTo(btn.getEl(), 'tl-bl');
                        }
                    },

                    '->',

                    // _TODEL_ Em razão do novo Dashboard, funcionalidade "Informações do usuário" transferida
                    // {
                    //     xtype: 'button',
                    //     enableToggle: true,
                    //     text: 'Informações do usuário',
                    //     xKey: 'user-info',
                    //     icon: '/' + global.Context + '/static/images/athenas-user-info.png',
                    //     //toggleGroup: 'btnsInfoUser',
                    //     scope: this,
                    //     toggleHandler: function(btn, st)
                    //     {
                    //         var windowInfo = toolkit.Application.getUserInformation();
                    //         if(st)
                    //         {
                    //             windowInfo.show();
                    //             windowInfo.alignTo(btn.getEl(), 'tr-br');
                    //         }
                    //         else
                    //             windowInfo.hide();
                    //     }
                    // },
                    toolkit.Application.getUserInformationButton(),
                    '-',

                    // _TODEL_ Em razão do novo Dashboard, funcionalidade "Notificações" transferida
                    {
                        hidden: true,
                        xtype: 'button',
                        id: 'cmp-tooltip-notifications',
                        enableToggle: true,
                        iconCls: 'icon-core icon-core-balloon-exclamation',
                        // text: 'Sem notificações',
                        toggleGroup: 'btnsInfoUser',
                        toggleHandler: function(btn, st)
                        {
                            if (st) {
                                toolkit.util.Notification.showAllNotifications(false);
                            } else {
                                toolkit.util.Notification.hideAllNotifications();
                            }
                        }
                    },
                    //'-',

                    {
                        xtype: 'button',
                        id: 'cmp-executions',
                        iconCls: 'icon-core icon-core-run',
                        enableToggle: true,
                        toggleGroup: 'btnsInfoUser',
                        toggleHandler: function(btn, st){
                            if(st){
                                toolkit.util.Tasks.getTasksForUser(
                                    true,
                                    function(){
                                        toolkit.util.Tasks.showAllTasks();
                                        toolkit.util.Tasks.updateInfoTasks();
                                    }
                                );
                                // toolkit.util.Tasks.showAllTasks();

                            }else{
                                toolkit.util.Tasks.hideAllTasks();

                            }
                        },
                        listeners: {
                            mouseover: function(btn, ev){
                                console.debug('MOUSE OVER...');
                            }
                        }

                    }
                ]
            },
            {
                region: 'center',
                layout: 'fit',
                items: toolkit.Application.tabspace
            },
            this.getMenuPanel(),
        ];

        return items;
    },

    startEventos: function() {
        var taskEvento = Ext.TaskMgr.start({
            'interval': (1000 * 600),
            'scope': {
                'locked': false,
                'doCheck': function(resource, interface) {
                    Ext.Ajax.request({
                        'url': core.callAction(resource),
                        'scope': this,
                        'success': function(request) {
                            var rst = Ext.decode(request.responseText);

                            if(rst.result) {
                                this.lockedCheck = false;
                                return;
                            }
                            else
                                Ext._create(interface, {
                                    'modal': true,
                                    'draggable': false,
                                    'listeners': {
                                        'scope': this,
                                        'destroy': function() {
                                            this.lockedCheck = false;
                                        }
                                    }
                                }).show();
                        }
                    });
                },
                'check': function(resource, interface) {
                    var t = Ext.TaskMgr.start({
                        'interval': 200,
                        'scope': this,
                        'run': function() {
                            if(!this.lockedCheck) {
                                this.lockedCheck = true;
                                this.doCheck(resource, interface);
                                Ext.TaskMgr.stop(t);
                            }
                            else
                                console.info('wait for check locked')
                        }
                    });
                }
            },
            'run': function() {
                if(!this.locked && !this.lockedCheck) {
                    var evt = Ext._create('engine.evento.Restful');
                    var cfg = evt.getRoute('active');

                    Ext.apply(cfg, {
                        'scope': this,
                        'success': function(request) {
                            var rst = Ext.decode(request.responseText);

                            Ext.each(
                                rst.collection,
                                function(row) {
                                    this.check(
                                        row.resource,
                                        row.interface
                                    );
                                },
                                this
                            );

                            this.locked = false;
                            Ext.TaskMgr.stop(taskEvento);
                        }
                    });

                    this.locked = true;
                    evt.doRequest(cfg);
                }
                else
                    console.debug('locked')
            }
        });
    },

    /**
     * Metodo utilizado para inicializar o Workspace.
     */
    start: function() {

        Ext.QuickTips.init();

        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
                'Application', 'get_session_information'
            ),
            method: 'GET',
            success: function(request) {
                var result = Ext.decode(request.responseText);

                if(result.is_auth  && result.is_firstaccess)
                    new toolkit.widget.ExtFirstAccess().show();
                else if(result.is_auth)
                    toolkit.Application.createWorkspace(result);
                else
                    toolkit.Application.createFormLogin();
            },
            waitMsg: 'Verificando sua sessão.'
        });
    },

    /**
     * Metodo de conformação do Layout.
     */
    conform: function() {
        var box = this.viewport.getBox();

        toolkit.Application.containers.functions.setHeight(box.height - 27);
        toolkit.Application.panels.center.getComponent(1).setHeight(box.height - 30);
    },

    /**
     * Finaliza a sessão.
     */
    endSession: function() {
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action("ExtLogin", "logout"),
            method: 'POST',
            success: function(xhr) {
                location.reload(true);
            },
            failure: function() {location.reload(true);}
        });
    }

}
