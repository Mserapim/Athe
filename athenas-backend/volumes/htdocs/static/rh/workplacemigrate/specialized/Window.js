Ext._define('rh.workplacemigrate.specialized.Window', {
    extend: 'rh.workplacemigrate.Window',

    rest: 'rh.workplacemigrate.specialized.Restful',

    width: 700,
    height: 640,

    _observe: function () {
        if (this.oId) {
            this.getTargetWorkplaceMigrateGrid().enable();
            this.getTargetWorkplaceMigrateGrid().setParam('workplace_migrate', this.oId);
            this.getTargetWorkplaceMigrateGrid().setFilterProperty('workplace_migrate', this.oId, 1001);
        }
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = rh.workplacemigrate.specialized.Window.superclass.getFormPanel.call(this, cfg);
            this._formPanel.insert(this._formPanel.items.length, this.getTargetWorkplaceMigrateGrid());
        }
        return this._formPanel;
    },

    getTargetWorkplaceMigrateGrid: function () {
        if (!this._targetWorkplaceMigrate) {
            this._targetWorkplaceMigrate = Ext._create(
                'rh.workplacemigrate.target.Grid',
                {
                    title: 'Apps impactado(s)',
                    height: 200,
                    stripeRows: true,
                    gridAutoLoad: false,
                    disabled: true,
                    hideActions: ['copy'],
                    configOrderToolBar: ['add', 'edit', 'remove', '-', 'autoInsert'],
                    autoInsertFieldWidth: 250
                }
            );
        }
        return this._targetWorkplaceMigrate;
    },

});

