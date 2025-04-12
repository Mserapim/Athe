Ext._define('planning.hiring.supervisor.MinuteSupervisorWindow', {
    extend: 'planning.hiring.supervisor.SupervisorWindow',
    rest: 'planning.hiring.supervisor.MinuteSupervisorRestful',
    relatedName: 'minutesupervisors',

    getButtons: function (cfg) {

        if (!this._buttons) {
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

            if (!cfg.disableSave)
                this._buttons = [{
                    text: 'Salvar',
                    scope: this,
                    handler: function () {

                        var me = this;
                        Ext.Ajax.request({
                            scope: this,
                            url: toolkit.util.Normalize.controller_action(
                                'PHMMinute',
                                'verify_minute_validity'
                            ),
                            params: {
                                minute: this.params.minute,
                            },
                            success: function (response) {
                                var obj = Ext.decode(response.responseText);
                                if (obj.success) {
                                    if (obj.after_end_validity)
                                        Ext.Msg.show({
                                            title: 'Ata fora da vigência',
                                            icon: Ext.Msg.QUESTION,
                                            buttons: Ext.Msg.YESNO,
                                            msg: obj.message,
                                            fn: function (bnt) {
                                                if (bnt == 'no') return;
                                                me.save(true);
                                            }
                                        });
                                    else
                                        me.save(true);
                                }
                                else
                                    Ext.Msg.show({
                                        title: 'Ata fora da vigência',
                                        icon: Ext.Msg.ERROR,
                                        buttons: Ext.Msg.OK,
                                        msg: obj.message
                                    });
                            },
                            failure: function (response) {
                                Ext.Msg.show({
                                    title: 'Ocorreu um erro. Tente novamente mais tarde.',
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK,
                                    msg: rst.message
                                });
                            }

                        });
                    },
                }].concat(this._buttons);

        }

        return this._buttons;
    },
});
