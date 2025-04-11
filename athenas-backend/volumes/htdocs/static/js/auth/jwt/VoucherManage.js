Ext._define('auth.jwt.VoucherManage', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Voucher'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getUserGrid(),
                    this.getVoucherGrid()
                ]
            }
        );

        auth.jwt.VoucherManage.superclass.constructor.call(this, cfg);
        this.observeUser();
    },

    user: function(value, observe) {
        observe = (observe === undefined ? true : observe);

        if(value !== undefined) {
            this._userGrid = value;

            if(observe)
                this.observeUser();
        }

        return this._userGrid;
    },

    observeUser: function() {
        var value = this.user();

        if(value) {
            this.getVoucherGrid().enable();
            this.getVoucherGrid().setParam('user', value.get('pk'));
            this.getVoucherGrid().setFilterProperty('user', value.get('pk'), 1000);
        } else  {
            this.getVoucherGrid().disable();
            this.getVoucherGrid().setParam('user', 0);
            this.getVoucherGrid().setFilterProperty('user', 0, 1000);
        }
    },

    getUserGrid: function(cfg) {
        if (!this._userGrid) {
            this._userGrid = Ext._create('auth.UserGrid', {
                region: 'center',
                width: '35%',
                minWidth: Ext.getBody().getBox().width * 0.25,
                maxWidth: Ext.getBody().getBox().width * 0.75,
                split: true,
                title: 'Usuário',
                configOrderToolBar: ['search', '->'],
                columnAction: false,
                onlyColumns: ['numberer', 'pessoa_nome_real', 'username'],
                doubleClickHandler: function() {},
                selModel: Ext._create('Ext.grid.RowSelectionModel', {singleSelect: true})
            });

            this._userGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                var selection = selm.getSelections();

                if(selection.length > 0)
                    this.user(selection[0]);
                else
                    this.user(null);
                }
            });

            this._userGrid.getStore().on({
                scope:this,
                load: function() {
                    this.observeUser();
                }
            });
        }

        return this._userGrid;
    },

    getVoucherGrid: function() {
        if(!this._voucherGrid) {
            this._voucherGrid = Ext._create('auth.jwt.VoucherGrid', {
                region: 'east',
                width: '65%',
                minWidth: Ext.getBody().getBox().width * 0.25,
                maxWidth: Ext.getBody().getBox().width * 0.75,
                split: true,
                title: 'Vouchers',
                configOrderToolBar: ['search', '->'],
                columnAction: false,
                onlyColumns: ['numberer', 'voucher_type_display', 'token'],
                doubleClickHandler: function() {},
                disabled: true,
                gridAutoLoad: false
            });
        }

        return this._voucherGrid;
    },
});
