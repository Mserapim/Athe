Ext._define('planning.hiring.ride.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.ride.Restful',

    width: 630,

    getRideItemGrid: function() {
        if(!this._rideItemGrid) {
            this._rideItemGrid = Ext._create('planning.hiring.rideitem.Grid', {
                title: 'Itens Adquiridos',
                region: 'south',
                height: 300,
                width: 610,
                gridAutoLoad: false,
            });
        }

        return this._rideItemGrid;
    },

    observeRide: function () {
        var value = this.ride();

        if (value) {
            this.getRideItemGrid().enable();
            this.getRideItemGrid().setParam('ride', value);
            this.getRideItemGrid().setParam('minute', this.values.minute);
            this.getRideItemGrid().setFilterProperty('ride', value, 0);
        } else {
            this.getRideItemGrid().disable();
            this.getRideItemGrid().setParam('ride', 0);
            this.getRideItemGrid().setParam('minute', 0);
            this.getRideItemGrid().setFilterProperty('ride', value, 0, false);
            this.getRideItemGrid().getStore().removeAll();
        }
    },

    ride: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._rideGrid = value;

            if (observe)
                this.observeRide();
        }

        return this._rideGrid;
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        name: "number",
                        xtype: "displayfield",
                        fieldLabel: "Carona",
                        width: 358,
                        allowBlank: true,
                    },
                    {
                        name: "minute",
                        fieldLabel: "Ata",
                        width: 490,
                        allowBlank: false,
                        xtype: "rest-autocompletefield",
                        rest: "planning.hiring.minute.MinuteRestful",
                        preFilter: [
                            {property: 'status__in', value: [1], stage: 1002}
                        ],
                    },
                    {
                        name: "person",
                        fieldLabel: "Nome",
                        width: 490,
                        allowBlank: false,
                        xtype: "rest-autocompletefield",
                        rest: "rh.person.legalperson.Restful",
                    },
                    {
                        width: 490,
                        allowBlank: false,
                        fieldLabel: "Documento",
                        name: "asking",
                        xtype: "textfield",
                    },
                    {
                        width: 490,
                        allowBlank: false,
                        fieldLabel: "Solicitação",
                        name: "asking_date",
                        xtype: "datefield",
                    },
                    {
                        width: 490,
                        allowBlank: true,
                        fieldLabel: "Acordo",
                        name: "agreement_date",
                        xtype: "datefield",
                    },
                    {
                        width: 490,
                        allowBlank: true,
                        fieldLabel: "Autorização",
                        name: "authorization_date",
                        xtype: "datefield",
                    },
                    {
                        width: 490,
                        allowBlank: true,
                        fieldLabel: "Despacho",
                        name: "dispatch_number",
                        xtype: "textfield",
                    },
                    this.getRideItemGrid()
                ]
            });

        return this._formPanel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.ride(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                    var ride = instance.pk;
                    var minute = instance.minute;
                    this.getRideItemGrid().enable();
                    this.getRideItemGrid().setParam('minute', minute);
                    this.getRideItemGrid().setParam('ride', ride);
                    this.getRideItemGrid().setFilterProperty('ride', ride, 0);
                }
            }
        });

        planning.hiring.ride.Window.superclass.constructor.call(this, cfg);
        this.ride(cfg.oId === undefined ? null : cfg.oId);
    },
});
