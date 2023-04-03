from rest_framework import serializers


class UserSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "id": obj.getId(),
            "first_name": obj.getFirstName(),
            "last_name": obj.getLastName(),
            "email": obj.getEmail(),
            "registration_status": obj.getRegistrationStatus(),
            "picture": obj.getPicture().__dict__,
            "default_currency": obj.getDefaultCurrency(),
            "locale": obj.getLocale(),
            "date_format": obj.getDateFormat(),
            "default_group_id": obj.getDefaultGroupId(),
        }


class BalanceSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "currency_code": obj.getCurrencyCode(),
            "amount": obj.getAmount(),
        }


class FriendSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "id": obj.getId(),
            "balances": BalanceSerializer(obj.getBalances(), many=True).data,
        }


class DebtSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "from": obj.getFromUser(),
            "to": obj.getToUser(),
            "amount": obj.getAmount(),
            "currency_code": obj.getCurrencyCode(),
        }


class GroupSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        members = FriendSerializer(obj.getMembers(), many=True).data
        simplified_debts = DebtSerializer(obj.getSimplifiedDebts(), many=True).data

        return {
            "id": obj.getId(),
            "name": obj.getName(),
            "updated_at": obj.getUpdatedAt(),
            "whiteboard": obj.getWhiteBoard(),
            "simplified_by_default": obj.isSimplifiedByDefault(),
            "members": members,
            "type": obj.getType(),
            "group_type": obj.getGroupType(),
            "simplified_debts": simplified_debts,
            "invite_link": obj.getInviteLink(),
        }


class CategorySerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "subcategories": CategorySerializer(obj.getSubcategories(), many=True).data,
            "id": obj.getId(),
            "name": obj.getName(),
        }


class CurrencySerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "code": obj.getCode(),
            "unit": obj.getUnit(),
        }


class DebtSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "from_user": obj.getFromUser(),
            "to_user": obj.getToUser(),
            "amount": obj.getAmount(),
            "currency_code": obj.getCurrencyCode(),
        }


class ExpenseUserSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "id": obj.getId(),
            "first_name": obj.getFirstName(),
            "last_name": obj.getLastName(),
            "email": obj.getEmail(),
            "registration_status": obj.getRegistrationStatus(),
            "picture": PictureSerializer(obj.getPicture()).data,
            "paid_share": obj.getPaidShare(),
            "owed_share": obj.getOwedShare(),
            "net_balance": obj.getNetBalance(),
        }


class ExpenseSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "id": obj.getId(),
            "group_id": obj.getGroupId(),
            "description": obj.getDescription(),
            "is_repeat": obj.isRepeat(),
            "repeat_interval": obj.getRepeatInterval(),
            "email_reminder": obj.getEmailReminder(),
            "email_reminder_in_advance": obj.getEmailReminderInAdvance(),
            "next_repeat": obj.getNextRepeat(),
            "details": obj.getDetails(),
            "comments_count": obj.getCommentsCount(),
            "payment": obj.getPayment(),
            "creation_method": obj.getCreationMethod(),
            "transaction_method": obj.getTransactionMethod(),
            "transaction_confirmed": obj.getTransactionConfirmed(),
            "cost": obj.getCost(),
            "currency_code": obj.getCurrencyCode(),
            "created_by": UserSerializer(obj.getCreatedBy()).data,
            "date": obj.getDate(),
            "created_at": obj.getCreatedAt(),
            "updated_at": obj.getUpdatedAt(),
            "deleted_at": obj.getDeletedAt(),
            "receipt": ReceiptSerializer(obj.getReceipt()).data,
            "category": CategorySerializer(obj.getCategory()).data,
            "updated_by": UserSerializer(obj.getUpdatedBy()).data,
            "deleted_by": UserSerializer(obj.getDeletedBy()).data,
            "users": ExpenseUserSerializer(obj.getUsers(), many=True).data,
            "expense_bundle_id": obj.getExpenseBundleId(),
            "friendship_id": obj.getFriendshipId(),
            "repayments": DebtSerializer(obj.getRepayments(), many=True).data,
        }


class PictureSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "small": obj.getSmall(),
            "medium": obj.getMedium(),
            "large": obj.getLarge(),
        }


class ReceiptSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "original": obj.getOriginal(),
            "large": obj.getLarge(),
        }


class CommentSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "id": obj.getId(),
            "content": obj.getContent(),
            "comment_type": obj.getCommentType(),
            "relation_type": obj.getRelationType(),
            "relation_id": obj.getRelationId(),
            "created_at": obj.getCreatedAt(),
            "deleted_at": obj.getDeletedAt(),
            "user": UserSerializer(obj.getUser()).data,
        }


class SourceSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "id": obj.getId(),
            "type": obj.getType(),
            "url": obj.getUrl(),
        }


class NotificationSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "id": obj.getId(),
            "content": obj.getContent(),
            "image_shape": obj.getImageShape(),
            "image_type": obj.getImageType(),
            "source": SourceSerializer(obj.source).data,
            "created_at": obj.getCreatedAt(),
            "created_by": obj.getCreatedBy(),
        }
