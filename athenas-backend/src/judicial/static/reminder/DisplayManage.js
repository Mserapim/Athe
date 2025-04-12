

Ext._define('judicial.reminder.DisplayManage', {
    xtype: 'judicial-reminder-display',

    container: function() {
        if (!this._container) {
            var $el = this.attached.getEl().dom;
            var box = this.attached.getBox();
            this._container = document.createElement('div');

            Ext.apply(this._container.style, {
                position: 'absolute',
                top: this.paddingTop + 'px',
                height: (box.height > 120 ? box.height - (this.paddingTop + this.paddingBottom) : 40).toString() + 'px',
            });

            $el.appendChild(this._container);
        }

        return this._container;
    },

    _destroyContainer: function() {
        if (this._container) {
            var $el = this.attached.getEl().dom;
            $el.removeChild(this._container);
            this._container = undefined;
        }
    },

    destroy: function () {
        this._destroyContainer();
        this.started = false;
        this.unRegisterObserver();
    },

    maxItems: function() {
        return Number.parseInt(this.container().offsetHeight / 42, 10);
    },

    factoryReminder: function(reminder) {
        var el = document.createElement('div');

        Ext.apply(el.style, {
            display: 'table',
            backgroundColor: reminder.color,
            borderRadius: '0 3px 3px 0',
            padding: '5px 10px',
            marginBottom: '10px',
            fontSize: '0.8rem',
            lineHeight: '1.5rem',
            boxShadow: '2px 2px 7px 2px #555'
        });

        el.addEventListener('click', function() {
            core.invokeCallback(
                (reminder.callback || { fn: Ext.emptyFn }),
                reminder
            );
        });

        var prepareTitle = reminder.title;

        if (prepareTitle.length > 20) {
            prepareTitle = prepareTitle.slice(0, 20) + '...';
        }

        el.innerHTML = prepareTitle;

        Ext._create('Ext.ToolTip', {
            target: el,
            anchor: 'left',
            title: reminder.title,
            html: reminder.content,
            dismissDelay: 0,
            closable: false
        });

        return el;
    },

    redraw: function() {
        this._destroyContainer();
        this.refreshView(
            this.lastCollection,
            this.lastTotal
        );
    },

    refreshView: function(collection, total) {
        var data = [].concat(collection);
        var container = this.container();
        var me = this;
        var limit = this.maxItems() - 2;
        var plus = 0;

        this.lastCollection = collection;
        this.lastTotal = total;

        if (limit < total) {
            plus = total - limit;
            data = data.slice(0, limit);

            data.push({
                title: 'Todos (+' + plus.toString() + ')',
                content: 'Veja todos os lembretes',
                color: '#d3e0f2',
                callback: {
                    fn: function() {
                        me.openReminder();
                    }
                }
            });
        } else {
            data.push({
                title: 'Todos',
                content: 'Veja todos os lembretes',
                color: '#d3e0f2',
                callback: {
                    fn: function () {
                        me.openReminder();
                    }
                }
            });
        }

        data.push({
            title: 'Novo Lembrete',
            content: 'Crie um novo lembrete.',
            color: '#d3e0f2',
            callback: {
                scope: this,
                fn: function () {
                    this.newReminder();
                }
            }
        });

        container.innerHTML = '';

        if (this.callback && this.callback.refreshView) {
            core.invokeCallback(this.callback.refreshView);
        }

        data
            .map(function(reminder) {
                if (!reminder.title) {
                    reminder.title = reminder.content;
                }

                return reminder
            })
            .map(function(reminder) {
                var colors = [
                    '#fff',        // undefined
                    '#ff9898',     // urgente
                    '#ffda98',     // rapido
                    '#c8ff9e'      // normal
                ];

                if (!reminder.color) {
                    reminder.color = colors[reminder.reminder_state] || colors[0];
                }

                return reminder;
            })
            .forEach(
                function (reminder) {
                    var reminderEl = me.factoryReminder(reminder);
                    container.appendChild(reminderEl);
                }
            );
    },

    defaultParams: function() { return {} },

    newReminder: function () {
        Ext._create(this.windowClass, {
            action: 'create',
            params: this.defaultParams(),
            callback: {
                success: {
                    scope: this,
                    fn: function (instance) {
                        this.refresh();

                        console.log(this.callback);
                        core.invokeCallback(
                            (this.callback.afterNew || { fn: Ext.emptyFn }),
                            instance
                        );
                    }
                }
            }
        }).show();
    },

    openReminder: function () {
        var mng = Ext._create(this.windowManageClass, {
            params: this.defaultParams(),
            modal: true
        });

        mng.on({
            scope: this,
            close: function () {
                console.log(['close', mng.dirty, this.callback]);

                if (mng.dirty) {
                    this.refresh();
                    core.invokeCallback((this.callback.afterChanges || { fn: Ext.emptyFn }));
                }
            }
        });

        mng.show();
    },

    refresh: function () {
        throw 'Abstract method not implemented';
    },

    registerObserver: function() {
        throw 'Abstract method not implemented';
    },

    unRegisterObserver: function() {
        throw 'Abstract method not implemented';
    },

    start: function() {
        if (!this.started)
            this.registerObserver();

        this.started = true;
        this.refresh();
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            paddingTop: 20,
            paddingBottom: 20,
            attached: null,
            align: 'left',
            callback: {},
            lastCollection: [],
            lastTotal: 0
        });

        cfg.started = false;

        Ext.apply(this, cfg);
    }
});

