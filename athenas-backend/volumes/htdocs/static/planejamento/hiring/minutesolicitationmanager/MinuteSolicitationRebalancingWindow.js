Ext._define('planning.hiring.minutesolicitationmanager.MinuteSolicitationRebalancingWindow', {
    extend: 'planning.hiring.minutesolicitation.MinuteSolicitationWindow',

    rest: 'planning.hiring.minutesolicitation.MinuteSolicitationRestful',
    resizable: false,
    width: 1000,
    autoHeight: true,

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                labelAlign: 'top',
                frame: true,
                items: [
                    this.getMinuteSolicitationItemGrid(),
                ]
            });

        return this._formPanel;
    },

    doubleClick: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            var rebalancingWindow = Ext._create(
                'planning.hiring.minutesolicitationmanager.SolicitationRebalancingWindow', {
                    params: {
                        solicitation_item: selected.id,
                        itemgrid: this,
                        item_data: {
                            description: selected.data.description,
                            brand: selected.data.brand,
                            unit_value: selected.data.brand,
                            is_rebalanced: selected.data.is_rebalanced
                        }
                    },
                    oId: selected.data.balanced_oid, 
                    values: 'remote'
            });

            rebalancingWindow.show();

            if(!selected.data.is_rebalanced) {
                rebalancingWindowForm = rebalancingWindow.getFormPanel().getForm();
                rebalancingWindowForm.findField('description').setValue(selected.data.description);
                rebalancingWindowForm.findField('brand').setValue(selected.data.brand);
                rebalancingWindowForm.findField('unit_value').setValue(selected.data.unit_value);
            }
        }
        else {
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item.'
            });
        }
    },

    getMinuteSolicitationItemGrid: function (cfg) {
        if (!this._minuteSolicitationItemPanel) {
            this._minuteSolicitationItemPanel = Ext._create('planning.hiring.minutesolicitation.MinuteSolicitationItemGrid', {
                title: 'Itens',
                region: 'center',
                frame: true,
                height: 300,
                doubleClickHandler: this.doubleClick,
                configOrderToolBar: [],
            });
        }
        return this._minuteSolicitationItemPanel;
    },

    observeMinuteSolicitation: function () {
        this.getMinuteSolicitationItemGrid().enable();
        this.getMinuteSolicitationItemGrid().setParam('solicitation', this.params.solicitation);
        this.getMinuteSolicitationItemGrid().setParam('minute', this.params.minute);
        this.getMinuteSolicitationItemGrid().setFilterProperty('solicitation', this.params.solicitation, 0);
    },

    getButtons: function (cfg) {

        if (!this._buttons) {
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];
        }

        return this._buttons;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.solicitation(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        planning.hiring.minutesolicitationmanager.MinuteSolicitationRebalancingWindow.superclass.constructor.call(this, cfg);

        this.observeMinuteSolicitation();
    }
});