Ext._define('core.dashboard.tasksondemand.DropdownMenu', {
    extend: 'Ext.Button',

    getIcon: function (cfg) {
        return ['/', global.Context, '/static/images/waiting.png'].join('');
    },

    _renderProgressOfRow: function(row, data) {
        var el = Ext.get(row);

        var container = Ext._create('Ext.Container', {
            autoEl: 'div',
            style: {
                padding: '0px 10px 10px 10px',
            },
            items: [{
                xtype: 'progress',
                value: (data.get('progress') / 100.0),
                text: data.get('progress_message'),
            }]
        });

        container.render(el);
    },

    _renderProgressForEachRow: function (store) {
        store.each(function (data) {
            var progress = data.get('progress');

            if (!Ext.isNumber(progress)) {
                return;
            }

            var index = this.getTaskGrid().getStore().indexOf(data);
            if (index === -1) {
                return;
            }

            var row = this.getTaskGrid().getView().getRow(index);

            this._renderProgressOfRow(row, data);
        }, this);
    },

    _taskGridLoadEvent: function(store, data) {
        this.updateCount(data.length);
        this._renderProgressForEachRow(store);
    },

    getTaskGrid: function(cfg) {
        if (this._taskGrid) {
            return this._taskGrid;
        }

        this._taskGrid = Ext._create('engine.mq.TaskGridCustom', {
            gridAutoLoad: false,
            width: 400,
            height: 500,
            frame: false,
            columnAction: false,
            configOrderToolBar: ['->', '-', 'autoLoadGrid', '-', 'finished', '-', 'finishedAll'],
        });

        var status = ['initializing', 'ready', 'failed', 'progress']
        this._taskGrid.setFilterProperty('state__in', status, 42, false);
        this._taskGrid.getStore().on({
            scope: this,
            load: this._taskGridLoadEvent,
        });

        return this._taskGrid;
    },

    handler: function (button, event) {
        this.getTaskGrid().getStore().reload();
    },

    updateCount: function (count) {
        var text = 'Relatórios';

        if (Ext.isNumber(count) && count > 0) {
            text = 'Relatórios (' + count + ')';
        }

        this.setText(text);
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            text: 'Tarefas sob demanda',
            icon: this.getIcon(cfg),
        });

        Ext.apply(cfg, {
            id: 'cmp-tasks-on-demand-menu',
            cls: 'button-highlight',  // texto negritado
            menu: [
                this.getTaskGrid(cfg),
            ],
        });

        core.dashboard
          .tasksondemand
          .DropdownMenu
          .superclass
          .constructor
          .call(this, cfg);
    }
});
