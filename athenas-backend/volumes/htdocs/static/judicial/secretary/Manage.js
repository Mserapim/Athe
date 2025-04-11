Ext._define('judicial.secretary.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getSecretaryGrid: function() {
        if(!this._secretaryGrid) {
            this._secretaryGrid = Ext._create('judicial.secretary.Grid', {
                region: 'center',
                minWidth: 500,
                hideItemsToolbar: ['download'],
            });

            this._secretaryGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data) {
                    this.secretary(data.get('pk'));
                },
                rowdeselect: function() {
                    this.secretary(null);
                }
            });
        }

        return this._secretaryGrid;
    },

    getExecutionOrganGrid: function() {
        if(!this._executionOrganGrid) {
            this._executionOrganGrid = Ext._create('judicial.county.ExecutionOrganGrid', {
                region: 'east',
                gridAutoLoad: false,
                minWidth: 650,
                width: Ext.getBody().getBox().width * 0.5,
                split: true,
                allowAdd: false,
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download'],
                onlyColumns: ['nome', 'owner_unicode'],
            });
        }

        return this._executionOrganGrid;
    },

    secretary: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._secretary = value;

            !prevent && this.observeSecretary();
        }

        return this._secretary;
    },

    observeSecretary: function() {
        var value = this.secretary();

        if(value) {
            this.getExecutionOrganGrid().enable();
            this.getExecutionOrganGrid().setFilterProperty(
                'as_secretaries',
                value,
                1001
            );
        }
        else {
            this.getExecutionOrganGrid().disable();
            this.getExecutionOrganGrid().setFilterProperty(
                'as_secretaries',
                0,
                1001,
                false
            );
            this.getExecutionOrganGrid().getStore().removeAll();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Secretarias'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getSecretaryGrid(),
                    this.getExecutionOrganGrid()
                ]
            }
        );

        judicial.secretary.Manage.superclass.constructor.call(this, cfg);
        this.secretary(null);
    }
});
