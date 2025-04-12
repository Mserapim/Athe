Ext._define('planning.hiring.minuteitem.MinuteItemWindowValidator', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minuteitem.MinuteItemValidatorRestful',
    resizable: false,
    width: 1000,
    autoHeigth: true,

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: true,
                frame: true,
                layout: 'form',
                autoHeight: true,
                items: [
                    this.getMinuteItemGridValidator(cfg),
                ],
                listeners: {
                    scope: this,
                    render: function () {
                        Ext.Ajax.request({
                            scope: this,
                            url: toolkit.util.Normalize.controller_action('PHMMinuteItem', 'get_total_value_imported'),
                            params: { minute: this.params.minute },
                            success: function (request) {
                                var obj = Ext.decode(request.responseText);
                                if (obj.success)
                                    this.getMinuteItemGridValidator(cfg).getTotalValueImportedItems().setText(obj.textValue);
                                else
                                    this.getMinuteItemGridValidator(cfg).getTotalValueImportedItems().setText('Total: Não disponível');
                            },
                            failure: function (request) {
                                this.getMinuteItemGridValidator(cfg).getTotalValueImportedItems().setText('Total: Não disponível');
                            }
                        });

                    }
                }

            });
        }

        return this._formPanel;

    },


    getMinuteItemGridValidator: function (cfg) {
        if (!this._minuteItemGridValidator) {
            this._minuteItemGridValidator = Ext._create('planning.hiring.minuteitem.MinuteItemGridValidator', {
                region: 'center',
                minWidth: '50%',
                height: 582,
                frame: true,
                columnAction: false,
            });
        }

        this._minuteItemGridValidator.setFilterProperty('minute', cfg.params.minute, 1000, false);
        this._minuteItemGridValidator.addFilterProperty('status', 5, 1001, false);

        return this._minuteItemGridValidator;
    },

    _validate: function () {

        Ext.Ajax.request({
            scope: this,
            url: toolkit.util.Normalize.controller_action('PHMMinuteItem', 'validate_items'),
            params: { minute: this.params.minute },
            success: function (request) {
                var obj = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Validar Importação',
                    icon: Ext.Msg.INFO,
                    buttons: Ext.Msg.OK,
                    msg: obj.message
                });
                this.gridItems.getStore().reload();
                this.destroy();
            },
            failure: function (request) {

                Ext.Msg.show({
                    title: 'Desfazer Importação',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: obj.message
                });
            }
        });

    },

    _invalidate: function () {
        Ext.Ajax.request({
            scope: this,
            url: toolkit.util.Normalize.controller_action('PHMMinuteItem', 'invalidate_items'),
            params: { minute: this.params.minute },
            success: function (request) {
                var obj = Ext.decode(request.responseText);

                Ext.Msg.show({
                    title: 'Desfazer Importação',
                    icon: Ext.Msg.INFO,
                    buttons: Ext.Msg.OK,
                    msg: obj.message
                });
                this.gridItems.getStore().reload();
                this.destroy();
            },
            failure: function (request) {

                Ext.Msg.show({
                    title: 'Desfazer Importação',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: obj.message
                });
            }
        });

    },

    getButtons: function (cfg) {
        if (!this._buttons) {
            this._buttons = [];
            if (!cfg.disableSave)
                this._buttons.push({
                    text: 'Validar',
                    scope: this,
                    handler: this._validate

                });
            this._buttons.push(
                {
                    text: 'Desfazer',
                    scope: this,
                    handler: this._invalidate
                }
            );
        }

        return this._buttons;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(
            cfg,
            {
                resizable: false,
                items: this.getFormPanel(cfg),
                buttons: this.getButtons(cfg),
                listeners: {
                    scope: this,
                    close: function () { this._invalidate() }
                }
            }
        );

        planning.hiring.minuteitem.MinuteItemWindowValidator.superclass.constructor.call(this, cfg);
    }
});
