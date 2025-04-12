
Ext._define('judicial.reminder.partlawsuit.DisplayManage', {
    extend: 'judicial.reminder.DisplayManage',

    windowClass: 'judicial.reminder.partlawsuit.Window',
    windowManageClass: 'judicial.reminder.partlawsuit.WindowManage',

    defaultParams: function() {
        return {
            part_lawsuit: this.partLawsuitId
        };
    },

    refresh: function () {
        var rest = Ext._create('judicial.reminder.partlawsuit.Restful');

        rest.doRequest(
            rest.getRoute('read', false, 'GET', {
                params: {
                    filter: Ext.encode([
                        { property: 'part_lawsuit', value: this.partLawsuitId, stage: 1 },
                        { property: 'deactivated_by__isnull', value: true, stage: 2 }
                    ]),
                    start: 0,
                    limit: 30
                },
                scope: this,
                success: function (xhr) {
                    var result = Ext.decode(xhr.responseText);
                    result.success && this.refreshView(result.collection, result.count);
                }
            })
        );
    },

    start: function () {
        if (!this.partLawsuitId) {
            console.error('Não foi informado o partLawsuitId não posso continuar');
        } else {
            judicial.reminder.partlawsuit.DisplayManage.superclass.start.call(this);
        }
    },

    registerObserver: function () {
        console.log('not implemented registerObserver method')
    },

    unRegisterObserver: function () {
        console.log('not implemented unRegisterObserver method')
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            lawsuitId: null,
        });

        if (!cfg.partLawsuitId) {
            throw 'Não foi definido o PartLawsuit ID.'
        }

        judicial.reminder.partlawsuit.DisplayManage.superclass.constructor.call(this, cfg);
    }
});
