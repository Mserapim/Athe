
Ext._define('engine.notify.Manage', {
    extend: 'Object',

    statics: {
        _db: [],

        register: function(name, Klass) {
            engine.notify.Manage._db.push({
                className: Klass,
                name: name
            });
        },
    },

    observe: function(notifications) {
        engine.notify.Manage._db.forEach(function(item) {
            var value = notifications[item.name];
            item.instance.counter(value);
        });
    },

    render: function() {
        var count = 0;

        engine.notify.Manage._db.forEach(function(item) {
            count += (eval(item.className).prototype.padding || 1);

            item.instance = Ext._create(item.className, {
                mgnPosition: count
            });
        });
    }
});

Ext._define('engine.notify.NotifyContainer', {
    extend: 'Ext.Container',

    padding: 1,

    bodyHeight: 200,

    actionIconCls: 'icon-core icon-core-run',

    _title: 'Undefined',

    title: function() {
        if(this.counter() > 0)
            return this._title + ' ('+ this.counter() + ')';
        else
            return this._title;
    },

    getBodyContainer: function(cfg) {
        if(!this._bodyContainer)
            this._bodyContainer = Ext._create('Ext.Container',
                {
                    autoEl: 'div',
                    style: {
                        border: '1pt solid #99bbe8',
                        borderTop: null,
                        backgroundColor: '#e9f2ff',
                        height: this.bodyHeight + 'px',
                        borderRadius: '0px 0px 4px 4px'
                    }
                }
            );

        return this._bodyContainer;
    },

    iconCounter: function() {
        return this.counter();
    },

    iconCode: function(value) {
        value = core.nullValue(value, this.iconCounter());

        if(value > 0)
            return '<div class="notify-icon ' + this.actionIconCls + '" ext:qtip="' + this.title() + '">' +
                       '<span>' +
                           (value < 100 ? value : '+99') +
                       '</span>' +
                   '</div>';
        else
            return '<div class="notify-icon ' + this.actionIconCls + '" ext:qtip="' + this.title() + '"></div>';
    },

    counter: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._counter = value;

            if(dispatch)
                this.observeCounter();
        }

        return this._counter;
    },

    observeCounter: function() {
        var value = this.counter();
        this.getActionContainer().removeAll();
        this.getActionContainer().add(this.factoryIconContainer());
        this.getActionContainer().doLayout();
    },

    factoryIconContainer: function() {
        return Ext._create('Ext.Container', {
            autoEl: 'div',
            html: this.iconCode()
        });
    },

    getActionContainer: function(cfg) {
        if(!this._actionContainer) {
            this._actionContainer = Ext._create('Ext.Container', {
                autoEl: 'div',
                style: {
                    border: '1pt solid #99bbe8',
                    borderTop: null,
                    backgroundColor: '#e9f2ff',
                    width: '50px',
                    height: '35px',
                    borderRadius: '0px 0px 4px 4px'
                },
                items: [
                    this.factoryIconContainer()
                ],
                listeners: {
                    scope: this,
                    render: function(c) {
                        c.getEl().on({
                            scope: this,
                            click: function() {
                                this.handler();
                            }
                        });
                    }
                }
            });
        }

        return this._actionContainer;
    },

    collapseBody: function(animate) {
        animate = core.nullValue(animate, true);
        var moviment = (this.getBodyContainer().getBox().height + 5);

        if(this.collapsed) {
            this.getEl().setStyle('zIndex', (Number.parseInt(this.getEl().getStyle('zIndex')) + 100));
            this.getEl().move('bottom', moviment, animate);
        }
        else {
            var me = this.getEl();

            if(animate)
                this.getEl().move('top', moviment, {
                    callback: function() {
                        me.setStyle('zIndex', (Number.parseInt(me.getStyle('zIndex')) - 100));
                    }
                });
            else
                this.getEl().move('top', moviment, false);

        }

        this.collapsed = !this.collapsed;
    },

    handler: function() {
        throw 'not implemented';
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                autoEl: 'div',
                style: {
                    position: 'absolute',
                    zIndex: (2000 + Number.parseInt(cfg.mgnPosition)),
                    top: '0',
                    width: '400px',
                    height: (this.bodyHeight + 50) +  'px',
                    left: ((Ext.getBody().getBox().width - 630) - (cfg.mgnPosition * 55)) + 'px'
                },
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                items: [
                    this.getBodyContainer(cfg),
                    {
                        xtype: 'container',
                        autoEl: 'div',
                        style: {
                            paddingRight: '10px'
                        },
                        layout: {
                            type: 'hbox',
                            pack: 'end'
                        },
                        items: [
                            this.getActionContainer()
                        ]
                    }
                ],
                collapsed: false,
                renderTo: Ext.getBody()
            }
        );

        engine.notify.NotifyContainer.superclass.constructor.call(this, cfg);
        this.collapseBody(false);
    }
});

Ext._define('engine.mq.TaskNotifyContainer', {
    extend: 'engine.notify.NotifyContainer',

    bodyHeight: 500,

    actionIconCls: 'icon-core icon-core-run',

    _title: 'Tarefas sob demanda',

    renderProgressInRow: function(data) {
        var index = this.getTaskGridRestful().getStore().indexOf(data);

        if(index >= 0) {
            var el = Ext.get(this.getTaskGridRestful().getView().getRow(index));
            var p = Ext._create('Ext.Container', {
                autoEl: 'div',
                style: {
                    padding: '0px 10px 10px 10px',
                },
                items: [
                    {
                        xtype: 'progress',
                        value: (data.get('progress') / 100.0),
                        text: data.get('progress_message')
                    }
                ]
            });

            p.render(el);
        }
    },

    getTaskGridRestful: function(cfg) {
        if(!this._gridTaskRestful) {
            this._gridTaskRestful = Ext._create('engine.mq.TaskGridCustom', {
                gridAutoLoad: false,
                height: this.bodyHeight ,
                width: 398,
                frame: true,
                columnAction: false,
                configOrderToolBar: ['->', '-', 'finished'],
            });

            this._gridTaskRestful.setFilterProperty('state__in', ['ready', 'failed', 'progress'], 1, false);
            this._gridTaskRestful.getStore().on({
                scope: this,
                load: function(store, data) {
                    this.counter(data.length);

                    store.each(
                        function(data) {
                            var progress = data.get('progress')
                            console.debug('PROGRESS: '+ progress);
                            if(Ext.isNumber(progress))
                                this.renderProgressInRow(data);
                        },
                        this
                    );
                }
            });

            // this._gridTaskRestful.on({
            //     scope: this,
            //     viewready: function() {
            //
            //     }
            // });
        }

        return this._gridTaskRestful;
    },

    handler: function() {
        if(this.collapsed)
            this.getTaskGridRestful().getStore().load();
        this.collapseBody();
    },

    getBodyContainer: function(cfg) {
        if(!this._bodyContainer) {
            this._bodyContainer = engine.mq.TaskNotifyContainer.superclass.getBodyContainer.call(this, cfg);

            this._bodyContainer.add(
                this.getTaskGridRestful(cfg)
            );
        }

        return this._bodyContainer;
    },

});

Ext._define('engine.mq.UpgradeNotifyContainer', {
    extend: 'engine.notify.NotifyContainer',

    actionIconCls: 'icon-core icon-core-update-manage',

    _title: 'Atualizações do Sistema',

    changes: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._changes = value;

            if(dispatch)
                this.observeChanges();
        }

        return this._changes;
    },

    iconCounter: function() {
        return this.changes();
    },

    observeChanges: function() {
        this.getActionContainer().removeAll();
        this.getActionContainer().add(this.factoryIconContainer());
        this.getActionContainer().doLayout();
    },

    handler: function() {
        if(this.changes() > 0)
            Ext.Msg.show({
                title: 'Atualização no sistema',
                msg: 'Existe uma atualização de sistema pendente, salve todos os seus trabalhos e recarregue o sistema (F5).' +
                     '<br/><br/>' +
                     'Deseja aplicar agora?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                fn: function(btn) {
                    if(btn == 'yes') location.reload();
                }
            });
    },

    counter: function(value, dispatch) {
        dispatch = core.nullValue(dispatch, true);

        if(value && this._counter && this._counter < value) {
            var changes = value - this._counter;

            if(this.changes() != changes) {
                this.changes(changes);
            }

        }
        else
            engine.mq.UpgradeNotifyContainer.superclass.counter.call(this, value, dispatch);
    }
});

// _TODEL_ Em razão do novo Dashboard, excluir botões de "Tarefas sob demanda" e "Atualizações do Sistema"
//engine.notify.Manage.register('tasker', 'engine.mq.TaskNotifyContainer');
//engine.notify.Manage.register('build', 'engine.mq.UpgradeNotifyContainer');
