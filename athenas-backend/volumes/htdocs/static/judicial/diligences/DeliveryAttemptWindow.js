Ext._define('judicial.diligences.DeliveryAttemptWindow', {
    extend: 'core.RestfulWindow',

    rest: 'judicial.diligences.DeliveryAttemptRestful',

    width:650,
    buttonAlign: 'left',
    autoClose: true,

    getMainFields: function() {
        return [
            {
                xtype: "choicefield",
                width: 465,
                fieldLabel: "Tipo de Veículo",
                allowBlank: false,
                hiddenName: "type_vehicle",
                choiceId: 'judicial.TYPE_VEHICLE',
                name: "type_vehicle"
            },
            {
                allowBlank: false,
                fieldLabel: "Saída para entrega",
                name: "exit_date",
                xtype: "tk-datetimefield",
            },
            {
                allowBlank: false,
                fieldLabel: "Retorno da entrega",
                name: "return_date",
                xtype: "tk-datetimefield"
            },
            {
                allowBlank: true,
                fieldLabel: "Momento da entrega",
                name: "delivery_date",
                xtype: "tk-datetimefield"
            },
            {
                allowBlank: false,
                fieldLabel: "Comprovante de Entrega",
                name: "file_delivery",
                xtype: "ged-fileuploadfield",
                width: 465
            }
        ];
    },

    getCancelDeliveryField: function() {
        if (!this._cancelDeliveryField) {
            this._cancelDeliveryField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Devolver pois não será possivel realizar a entrega',
                name: 'cancel_delivery'
            });
        }

        return this._cancelDeliveryField;
    },

    getComplementaryFields: function() {
        return [
            this.getCancelDeliveryField(),
            {
                xtype: "choicefield",
                width: 465,
                fieldLabel: "Motivo da devolução",
                allowBlank: true,
                hiddenName: "cancel_delivery_type",
                choiceId: 'judicial.DELIVERY_CANCELATION_REASON',
                name: "cancel_delivery_type"
            },
            {
                xtype: 'container',
                items: [
                    {
                        allowBlank: false,
                        name: "observation",
                        xtype: "ckeditor"
                    }
                ]
            }
        ];
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 150,
                items: [
                    this.getMainFields(),
                    this.getComplementaryFields()
                ]
            });

        return this._formPanel;
    },

    _prepareToSign: function() {
        var originalCallback = this.callback;

        this.callback = {
            success: {
                scope: this,
                fn: function (instance) {
                    var me = this;
                    this.callback = originalCallback;

                    setTimeout(
                        function () { me._sign(); },
                        50
                    );
                }
            }
        };

        this.save(true);
    },

    sign: function() {
        Ext.Msg.show({
            title: 'Assinando',
            msg: [
                'Tem certeza que deseja assinar esta',
                'tentativa de entrega?'].join(''),
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if (btn === 'yes') this._prepareToSign();
            }
        });
    },

    _sign: function() {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Assinando documento...' });

        mask.show();
        this.factoryRestful().signAttempt(this.oId, {
            success: {
                scope: this,
                fn: function(retorno){
                    Ext.Msg.show({
                        title: 'Assinando documento',
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK,
                        msg: 'Documento assinado com sucesso.'
                    });

                    if(this.autoClose)
                        this.close();

                    if (this.ownerGrid) {
                        this.ownerGrid.fireEvent('afterSignSuccess', rst.instance);
                    }
                    
                    core.invokeCallback((this.callback || {}).success, rst.instance);
                }
            },
            failure: {
                fn: function(message){
                    Ext.Msg.show({
                        title: 'Assinando Documento',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                    if(this.buttons)
                        this.buttons.forEach(function(btn) { btn.enable(); });
                }
            },
            complete: {
                fn: function(retorno){
                    mask.hide();
                }
            }
        });
    },

    getLeftButtons: function(cfg) {
        if(!this._leftButtons)
            this._leftButtons = [
                {
                    text: 'Assinar',
                    scope: this,
                    handler: this.sign
                }
            ];

        return this._leftButtons;
    },

    getRightButtons: function(cfg) {
        if(!this._rightButtons)
            this._rightButtons = judicial.diligences.DeliveryAttemptWindow.superclass.getButtons.call(this, cfg);

        return this._rightButtons;
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            var groupButton;
            groupButton = this.getLeftButtons(cfg);
            groupButton.push('->');
            this._buttons = groupButton.concat(this.getRightButtons(cfg));
        }

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(obj) {
                    this.oId = obj.pk;
                    this.action = 'update';
                }
            }
        });

        judicial.diligences.DeliveryAttemptWindow.superclass.constructor.call(this, cfg);
    }
});
