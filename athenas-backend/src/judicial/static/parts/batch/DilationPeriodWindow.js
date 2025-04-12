Ext._define('judicial.parts.batch.DilationPeriodWindow', {
    extend: 'judicial.parts.DilationPeriodWindow',

    rest: 'judicial.parts.DilationPeriodRestful',

    width: 900,

    actionTitle: 'Dilação de Prazo em bloco',

    dilationBatch: function() {
        var mask = new Ext.LoadMask(Ext.getBody(), { msg: 'Alterando prazos de procedimentos...' });

        mask.show();

        Ext.Ajax.request({
            url: core.callAction('EJudDilationPeriod', 'dilation_batch'),
            params: this.getParams(),
            method: 'POST',
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);

                if (rst.success) {
                    Ext.Msg.show({
                        title: 'Envio de procedimentos em bloco',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                }
                else
                    Ext.Msg.show({
                        title: 'Erro na alteração de prazos de procedimentos',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Falha',
                    msg: 'Falha na alteração de prazos de procedimentos. Nenhum procedimento foi alterado.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    show: function () {
        if (this.action === 'create')
            Ext.Msg.show({
                title: 'Registrando ' + this.actionTitle,
                msg: 'Tem certeza que deseja registrar "' + this.actionTitle + '""?',
                scope: this,
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                fn: function (btn) {
                    if (btn === 'no') return;
                    this.dilationBatch();
                }
            });
        else
            Ext.Msg.show({
                title: 'Registrando ' + this.actionTitle,
                msg: this.actionTitle + ', não permite edição.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        judicial.parts.batch.DilationPeriodWindow.superclass.constructor.call(this, cfg);
    }
});
